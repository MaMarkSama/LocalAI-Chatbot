"""Accurate token, request and search analytics.

New requests are stored as immutable events.  Legacy message token columns are
kept and backfilled in reports, so existing installations retain their history.
"""
from __future__ import annotations

import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from database import db


logger = logging.getLogger(__name__)


class UsageTracker:
    def __init__(self):
        self._init_schema()

    def _init_schema(self) -> None:
        conn = db._conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS usage_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT NOT NULL UNIQUE,
                message_id INTEGER,
                user_id TEXT,
                session_id TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'webchat',
                model TEXT,
                operation TEXT NOT NULL DEFAULT 'chat',
                prompt_tokens INTEGER NOT NULL DEFAULT 0,
                completion_tokens INTEGER NOT NULL DEFAULT 0,
                total_tokens INTEGER NOT NULL DEFAULT 0,
                duration_ms INTEGER NOT NULL DEFAULT 0,
                web_search INTEGER NOT NULL DEFAULT 0,
                library_search INTEGER NOT NULL DEFAULT 0,
                search_results INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'ok',
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_usage_user_created
                ON usage_events(user_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_usage_created
                ON usage_events(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_usage_message
                ON usage_events(message_id);

            CREATE TABLE IF NOT EXISTS search_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                session_id TEXT,
                query TEXT NOT NULL,
                planned_queries INTEGER NOT NULL DEFAULT 1,
                result_count INTEGER NOT NULL DEFAULT 0,
                fetched_pages INTEGER NOT NULL DEFAULT 0,
                duration_ms INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'ok',
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_search_created
                ON search_events(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_search_user_created
                ON search_events(user_id, created_at DESC);
        """)
        conn.commit()

    @staticmethod
    def _non_negative(value: int) -> int:
        try:
            return max(0, int(value or 0))
        except (TypeError, ValueError):
            return 0

    def record_usage(
        self,
        session_id: str,
        prompt_tokens: int,
        completion_tokens: int,
        *,
        message_id: Optional[int] = None,
        user_id: Optional[str] = None,
        source: str = "webchat",
        model: str = "",
        operation: str = "chat",
        duration_ms: int = 0,
        web_search: bool = False,
        library_search: bool = False,
        search_results: int = 0,
        status: str = "ok",
        request_id: Optional[str] = None,
    ) -> Optional[int]:
        prompt = self._non_negative(prompt_tokens)
        completion = self._non_negative(completion_tokens)
        conn = db._conn()
        try:
            if message_id is None and operation == "chat":
                row = conn.execute(
                    "SELECT id FROM messages WHERE session_id = ? AND role = 'assistant' ORDER BY id DESC LIMIT 1",
                    (session_id,),
                ).fetchone()
                message_id = int(row["id"]) if row else None
            if message_id is not None:
                conn.execute(
                    "UPDATE messages SET prompt_tokens = ?, completion_tokens = ? WHERE id = ? AND session_id = ?",
                    (prompt, completion, message_id, session_id),
                )
            if user_id is None:
                user_id = db.get_session_owner(session_id)
            cursor = conn.execute("""
                INSERT OR IGNORE INTO usage_events
                (request_id, message_id, user_id, session_id, source, model, operation,
                 prompt_tokens, completion_tokens, total_tokens, duration_ms,
                 web_search, library_search, search_results, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request_id or secrets.token_urlsafe(16), message_id, user_id, session_id,
                source or "unknown", model, operation or "chat", prompt, completion,
                prompt + completion, self._non_negative(duration_ms), int(bool(web_search)),
                int(bool(library_search)), self._non_negative(search_results), status or "ok",
                datetime.now().isoformat(timespec="seconds"),
            ))
            conn.commit()
            return int(cursor.lastrowid) if cursor.rowcount else None
        except Exception:
            logger.exception("Error recording usage")
            conn.rollback()
            return None

    def record_search(self, user_id: Optional[str], session_id: str, report: Dict) -> None:
        try:
            conn = db._conn()
            conn.execute("""
                INSERT INTO search_events
                (user_id, session_id, query, planned_queries, result_count,
                 fetched_pages, duration_ms, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, session_id, str(report.get("query", ""))[:1000],
                len(report.get("queries") or []), len(report.get("sources") or []),
                self._non_negative(report.get("fetched_pages", 0)),
                self._non_negative(report.get("duration_ms", 0)),
                str(report.get("status", "unknown"))[:30],
                datetime.now().isoformat(timespec="seconds"),
            ))
            conn.commit()
        except Exception:
            logger.exception("Error recording search analytics")

    @staticmethod
    def _usage_union_sql(where: str = "", alias: str = "") -> str:
        prefix = f"{alias}." if alias else ""
        return f"""
            SELECT ue.user_id, ue.prompt_tokens, ue.completion_tokens, ue.created_at
            FROM usage_events ue
            {where}
            UNION ALL
            SELECT s.user_id, COALESCE(m.prompt_tokens, 0), COALESCE(m.completion_tokens, 0), m.created_at
            FROM messages m
            JOIN sessions s ON s.id = m.session_id
            WHERE m.role = 'assistant'
              AND (m.prompt_tokens IS NOT NULL OR m.completion_tokens IS NOT NULL)
              AND NOT EXISTS (SELECT 1 FROM usage_events linked WHERE linked.message_id = m.id)
        """

    def get_user_stats(self, user_id: str, days: int = 30) -> Dict:
        days = max(1, min(int(days), 3650))
        since = (datetime.now() - timedelta(days=days - 1)).date().isoformat()
        conn = db._conn()
        try:
            union_sql = self._usage_union_sql()
            row = conn.execute(f"""
                SELECT COALESCE(SUM(prompt_tokens), 0) AS total_input,
                       COALESCE(SUM(completion_tokens), 0) AS total_output,
                       COUNT(*) AS requests
                FROM ({union_sql}) all_usage
                WHERE user_id = ?
            """, (user_id,)).fetchone()
            daily = conn.execute(f"""
                SELECT substr(created_at, 1, 10) AS day,
                       SUM(prompt_tokens) AS input_tokens,
                       SUM(completion_tokens) AS output_tokens,
                       COUNT(*) AS requests
                FROM ({union_sql}) all_usage
                WHERE user_id = ? AND substr(created_at, 1, 10) >= ?
                GROUP BY substr(created_at, 1, 10)
                ORDER BY day
            """, (user_id, since)).fetchall()
            search_row = conn.execute("""
                SELECT COUNT(*) AS searches, COALESCE(SUM(result_count), 0) AS sources
                FROM search_events WHERE user_id = ?
            """, (user_id,)).fetchone()
            total_input = int(row["total_input"] or 0)
            total_output = int(row["total_output"] or 0)
            return {
                "user_id": user_id,
                "input_tokens": total_input,
                "output_tokens": total_output,
                "total_tokens": total_input + total_output,
                "requests": int(row["requests"] or 0),
                "messages": int(row["requests"] or 0),  # backward compatibility
                "web_searches": int(search_row["searches"] or 0),
                "search_sources": int(search_row["sources"] or 0),
                "daily": [dict(item) for item in daily],
            }
        except Exception as exc:
            logger.exception("Error getting user stats")
            return {"error": str(exc)}

    def get_all_usage(self) -> List[Dict]:
        try:
            union_sql = self._usage_union_sql()
            rows = db._conn().execute(f"""
                SELECT all_usage.user_id, u.username, u.display_name,
                       SUM(all_usage.prompt_tokens) AS input,
                       SUM(all_usage.completion_tokens) AS output,
                       COUNT(*) AS requests
                FROM ({union_sql}) all_usage
                LEFT JOIN users u ON all_usage.user_id = u.id
                GROUP BY all_usage.user_id
                ORDER BY SUM(all_usage.prompt_tokens + all_usage.completion_tokens) DESC
            """).fetchall()
            return [dict(row) for row in rows]
        except Exception:
            logger.exception("Error getting all usage")
            return []

    def get_admin_dashboard(self, days: int = 30) -> Dict:
        days = max(1, min(int(days), 365))
        since = (datetime.now() - timedelta(days=days - 1)).date().isoformat()
        conn = db._conn()
        union_sql = self._usage_union_sql()
        totals = conn.execute(f"""
            SELECT COALESCE(SUM(prompt_tokens), 0) AS input_tokens,
                   COALESCE(SUM(completion_tokens), 0) AS output_tokens,
                   COUNT(*) AS requests
            FROM ({union_sql}) all_usage
            WHERE substr(created_at, 1, 10) >= ?
        """, (since,)).fetchone()
        counts = conn.execute("""
            SELECT
              (SELECT COUNT(*) FROM users) AS users,
              (SELECT COUNT(*) FROM users WHERE is_active = 1) AS active_accounts,
              (SELECT COUNT(*) FROM sessions) AS sessions,
              (SELECT COUNT(*) FROM messages) AS messages,
              (SELECT COUNT(DISTINCT user_id) FROM sessions
                 WHERE updated_at >= datetime('now', '-1 day')) AS active_24h
        """).fetchone()
        daily = conn.execute(f"""
            SELECT substr(created_at, 1, 10) AS day,
                   SUM(prompt_tokens) AS input_tokens,
                   SUM(completion_tokens) AS output_tokens,
                   COUNT(*) AS requests
            FROM ({union_sql}) all_usage
            WHERE substr(created_at, 1, 10) >= ?
            GROUP BY substr(created_at, 1, 10) ORDER BY day
        """, (since,)).fetchall()
        by_model = conn.execute("""
            SELECT COALESCE(NULLIF(model, ''), 'legacy/unknown') AS label,
                   SUM(total_tokens) AS tokens, COUNT(*) AS requests
            FROM usage_events WHERE substr(created_at, 1, 10) >= ?
            GROUP BY COALESCE(NULLIF(model, ''), 'legacy/unknown') ORDER BY tokens DESC LIMIT 12
        """, (since,)).fetchall()
        by_source = conn.execute("""
            SELECT source AS label, SUM(total_tokens) AS tokens, COUNT(*) AS requests
            FROM usage_events WHERE substr(created_at, 1, 10) >= ?
            GROUP BY source ORDER BY tokens DESC
        """, (since,)).fetchall()
        searches = conn.execute("""
            SELECT COUNT(*) AS searches, COALESCE(SUM(result_count), 0) AS sources,
                   COALESCE(AVG(duration_ms), 0) AS avg_duration_ms,
                   COALESCE(SUM(CASE WHEN status = 'ok' THEN 1 ELSE 0 END), 0) AS successful
            FROM search_events WHERE substr(created_at, 1, 10) >= ?
        """, (since,)).fetchone()
        total_in = int(totals["input_tokens"] or 0)
        total_out = int(totals["output_tokens"] or 0)
        return {
            "period_days": days,
            "since": since,
            "totals": {
                **dict(counts),
                "input_tokens": total_in,
                "output_tokens": total_out,
                "total_tokens": total_in + total_out,
                "requests": int(totals["requests"] or 0),
            },
            "daily": [dict(row) for row in daily],
            "by_model": [dict(row) for row in by_model],
            "by_source": [dict(row) for row in by_source],
            "search": dict(searches),
            "users": self.get_all_usage(),
        }


usage_tracker = UsageTracker()
