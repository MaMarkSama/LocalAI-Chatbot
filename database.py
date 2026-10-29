"""
database.py — SQLite history manager
เก็บประวัติการสนทนาทั้ง Line Bot และ Web Chat
"""
import re
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from gemma_app.config import DB_PATH as APP_DB_PATH

DB_PATH = str(APP_DB_PATH)


class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = str(db_path)
        self._local  = threading.local()
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30)
            self._local.conn.execute("PRAGMA journal_mode=WAL;")
            self._local.conn.execute("PRAGMA foreign_keys=ON;")
            self._local.conn.execute("PRAGMA busy_timeout=30000;")
            self._local.conn.execute("PRAGMA synchronous=NORMAL;")
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _init_db(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            conn.execute("PRAGMA foreign_keys=ON;")
            conn.execute("PRAGMA busy_timeout=30000;")
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id          TEXT PRIMARY KEY,
                    user_id     TEXT,
                    source      TEXT NOT NULL DEFAULT 'webchat',
                    created_at  TEXT NOT NULL,
                    updated_at  TEXT NOT NULL,
                    title       TEXT
                );
                CREATE TABLE IF NOT EXISTS messages (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id  TEXT    NOT NULL,
                    role        TEXT    NOT NULL,
                    content     TEXT    NOT NULL,
                    created_at  TEXT    NOT NULL,
                    prompt_tokens     INTEGER,
                    completion_tokens INTEGER,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                );
                CREATE INDEX IF NOT EXISTS idx_messages_session
                    ON messages(session_id, id);
                CREATE INDEX IF NOT EXISTS idx_sessions_user_source_updated
                    ON sessions(user_id, source, updated_at DESC);
                CREATE INDEX IF NOT EXISTS idx_messages_session_role
                    ON messages(session_id, role, id);

                CREATE TABLE IF NOT EXISTS user_memories (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id    TEXT NOT NULL,
                    session_id TEXT,
                    type       TEXT NOT NULL,
                    content    TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_memories_user
                    ON user_memories(user_id, type);
                CREATE INDEX IF NOT EXISTS idx_memories_user_session
                    ON user_memories(user_id, session_id, id);

                CREATE TABLE IF NOT EXISTS user_files (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id     TEXT NOT NULL,
                    filename    TEXT NOT NULL,
                    file_hash   TEXT NOT NULL,
                    file_type   TEXT,
                    file_summary TEXT,
                    created_at  TEXT NOT NULL,
                    UNIQUE(user_id, file_hash)
                );
                CREATE INDEX IF NOT EXISTS idx_user_files_user_created
                    ON user_files(user_id, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_user_files_user_hash
                    ON user_files(user_id, file_hash);
            """)

            # migrate: add token columns if missing
            try:
                conn.execute("ALTER TABLE messages ADD COLUMN prompt_tokens INTEGER")
                conn.execute("ALTER TABLE messages ADD COLUMN completion_tokens INTEGER")
                conn.commit()
            except Exception: pass

            # migrate: add title column if missing
            try:
                conn.execute("ALTER TABLE sessions ADD COLUMN title TEXT")
                conn.commit()
            except Exception:
                pass

            for ddl in (
                "ALTER TABLE sessions ADD COLUMN project_id TEXT",
                "ALTER TABLE user_memories ADD COLUMN project_id TEXT",
                "ALTER TABLE user_files ADD COLUMN project_id TEXT",
                "ALTER TABLE user_files ADD COLUMN content_preview TEXT",
            ):
                try:
                    conn.execute(ddl)
                    conn.commit()
                except Exception:
                    pass

            # Full-text index for fast per-user chat history search. Some
            # custom SQLite builds omit FTS5, so LIKE remains as a fallback.
            try:
                fts_exists = conn.execute(
                    "SELECT 1 FROM sqlite_master WHERE name = 'messages_fts'"
                ).fetchone() is not None
                conn.executescript("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
                        content, content='messages', content_rowid='id', tokenize='unicode61'
                    );
                    CREATE TRIGGER IF NOT EXISTS messages_fts_ai AFTER INSERT ON messages BEGIN
                        INSERT INTO messages_fts(rowid, content) VALUES (new.id, new.content);
                    END;
                    CREATE TRIGGER IF NOT EXISTS messages_fts_ad AFTER DELETE ON messages BEGIN
                        INSERT INTO messages_fts(messages_fts, rowid, content)
                        VALUES ('delete', old.id, old.content);
                    END;
                    CREATE TRIGGER IF NOT EXISTS messages_fts_au AFTER UPDATE OF content ON messages BEGIN
                        INSERT INTO messages_fts(messages_fts, rowid, content)
                        VALUES ('delete', old.id, old.content);
                        INSERT INTO messages_fts(rowid, content) VALUES (new.id, new.content);
                    END;
                """)
                if not fts_exists:
                    conn.execute("INSERT INTO messages_fts(messages_fts) VALUES ('rebuild')")
            except sqlite3.OperationalError:
                pass
            conn.commit()

    def ensure_session(self, session_id: str, source: str = "webchat",
                       user_id: str = None, project_id: str = None):
        now  = datetime.now().isoformat()
        conn = self._conn()
        # Migration: หากเจ้าของเดิมเป็น anon และคนใหม่เป็น user จริง ให้ย้ายความจำตามมาด้วย
        old_owner = self.get_session_owner(session_id)
        if user_id and old_owner and old_owner.startswith("anon_") and old_owner != user_id:
            conn.execute("UPDATE user_memories SET user_id = ? WHERE user_id = ?", (user_id, old_owner))
            conn.execute("UPDATE sessions SET user_id = ? WHERE id = ?", (user_id, session_id))

        conn.execute("""
            INSERT INTO sessions (id, user_id, source, created_at, updated_at, project_id)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                updated_at = excluded.updated_at,
                project_id = COALESCE(excluded.project_id, sessions.project_id),
                user_id = CASE 
                    WHEN excluded.user_id IS NOT NULL AND (sessions.user_id IS NULL OR sessions.user_id LIKE 'anon_%') 
                    THEN excluded.user_id 
                    ELSE sessions.user_id 
                 END
        """, (session_id, user_id, source, now, now, project_id))
        conn.commit()

    def rename_session(self, session_id: str, title: str):
        conn = self._conn()
        conn.execute("UPDATE sessions SET title = ? WHERE id = ?", (title, session_id))
        conn.commit()

    def add_message(self, session_id: str, role: str, content: str, source: str = "webchat",
                    user_id: str = None, project_id: str = None):
        self.ensure_session(session_id, source, user_id=user_id, project_id=project_id)
        now  = datetime.now().isoformat()
        conn = self._conn()
        cursor = conn.execute(
            "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (session_id, role, content, now)
        )
        conn.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (now, session_id))
        conn.commit()
        return int(cursor.lastrowid)

    def get_messages(self, session_id: str, limit: int = 20) -> List[Dict]:
        conn = self._conn()
        rows = conn.execute("""
            SELECT role, content FROM (
                SELECT role, content, id FROM messages
                WHERE session_id = ?
                ORDER BY id DESC LIMIT ?
            ) ORDER BY id ASC
        """, (session_id, limit * 2)).fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in rows]

    def clear_session(self, session_id: str):
        conn = self._conn()
        conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        conn.commit()

    def delete_session(self, session_id: str):
        conn = self._conn()
        if self._table_exists("document_vectors"):
            conn.execute("DELETE FROM document_vectors WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM user_memories WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()

    def get_sessions(self, source: Optional[str] = None, limit: int = 100, user_id: str = None) -> List[Dict]:
        conn  = self._conn()
        query = """
            SELECT s.id, s.user_id, s.source, s.created_at, s.updated_at, s.title,
                   COUNT(m.id) as msg_count,
                   MAX(CASE WHEN m.role='user' THEN m.content END) as last_user_msg
            FROM sessions s
            LEFT JOIN messages m ON s.id = m.session_id
            WHERE 1=1
        """
        args = []
        if source:
            query += " AND s.source = ?"
            args.append(source)
        if user_id:
            query += " AND s.user_id = ?"
            args.append(user_id)
        else:
            # ถ้าไม่ระบุ user (Guest) ให้เห็นเฉพาะ session ที่ไม่มีเจ้าของ (ซึ่งจะถูกกรองต่อในหน้าเว็บ)
            query += " AND (s.user_id IS NULL OR s.user_id LIKE 'anon_%')"
            
        query += " GROUP BY s.id ORDER BY s.updated_at DESC LIMIT ?"
        args.append(limit)
        rows = conn.execute(query, args).fetchall()
        return [dict(r) for r in rows]

    def get_session_owner(self, session_id: str) -> Optional[str]:
        row = self._conn().execute(
            "SELECT user_id FROM sessions WHERE id = ?",
            (session_id,)
        ).fetchone()
        return row["user_id"] if row else None

    def get_session(self, session_id: str) -> Optional[Dict]:
        row = self._conn().execute(
            "SELECT id, user_id, source, created_at, updated_at, title, project_id FROM sessions WHERE id = ?",
            (session_id,),
        ).fetchone()
        return dict(row) if row else None

    def get_session_messages(self, session_id: str) -> List[Dict]:
        conn = self._conn()
        rows = conn.execute("""
            SELECT role, content, created_at FROM messages
            WHERE session_id = ? ORDER BY id ASC
        """, (session_id,)).fetchall()
        return [dict(r) for r in rows]

    def search_messages(self, keyword: str, limit: int = 30, user_id: str = None) -> List[Dict]:
        conn = self._conn()
        clean = re.sub(r"\s+", " ", (keyword or "")).strip()[:300]
        if not clean:
            return []
        limit = max(1, min(int(limit), 100))
        tokens = re.findall(r"[\w\u0E00-\u0E7F]{2,}", clean, flags=re.UNICODE)
        if tokens and self._table_exists("messages_fts"):
            match_query = " AND ".join(
                f'"{token.replace(chr(34), chr(34) * 2)}"*' for token in tokens[:12]
            )
            try:
                query = """
                    SELECT m.session_id, m.role, m.content, m.created_at,
                           s.source, s.title, bm25(messages_fts) AS rank
                    FROM messages_fts
                    JOIN messages m ON m.id = messages_fts.rowid
                    JOIN sessions s ON m.session_id = s.id
                    WHERE messages_fts MATCH ?
                """
                args: List = [match_query]
                if user_id:
                    query += " AND s.user_id = ?"
                    args.append(user_id)
                query += " ORDER BY rank, m.id DESC LIMIT ?"
                args.append(limit)
                rows = [dict(row) for row in conn.execute(query, args).fetchall()]
                if rows:
                    return rows
            except sqlite3.OperationalError:
                pass

        query = """
            SELECT m.session_id, m.role, m.content, m.created_at, s.source, s.title
            FROM messages m
            JOIN sessions s ON m.session_id = s.id
            WHERE m.content LIKE ? ESCAPE '\\'
        """
        escaped = clean.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        args = [f"%{escaped}%"]
        if user_id:
            query += " AND s.user_id = ?"
            args.append(user_id)
        query += " ORDER BY m.id DESC LIMIT ?"
        args.append(limit)
        return [dict(row) for row in conn.execute(query, args).fetchall()]


    # ── Memory ────────────────────────────────────────────────────────────
    def save_memory(self, user_id: str, session_id: Optional[str],
                    mem_type: str, content: str):
        """บันทึก memory (summary หรือ fact)"""
        now  = datetime.now().isoformat()
        conn = self._conn()
        conn.execute("""
            INSERT INTO user_memories (user_id, session_id, type, content, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, session_id, mem_type, content, now))
        conn.commit()

    def get_memories(self, user_id: str, session_id: Optional[str] = None,
                     limit: int = 10) -> List[Dict]:
        """ดึง memory ของ user"""
        conn  = self._conn()
        query = """
            SELECT type, content, created_at FROM user_memories
            WHERE user_id = ?
        """
        args = [user_id]
        if session_id:
            query += " AND (session_id = ? OR session_id IS NULL)"
            args.append(session_id)
        query += " ORDER BY id DESC LIMIT ?"
        args.append(limit)
        rows = conn.execute(query, args).fetchall()
        return [dict(r) for r in reversed(rows)]

    def clear_memories(self, user_id: str, session_id: Optional[str] = None):
        conn = self._conn()
        if session_id:
            conn.execute(
                "DELETE FROM user_memories WHERE user_id = ? AND session_id = ?",
                (user_id, session_id))
        else:
            conn.execute("DELETE FROM user_memories WHERE user_id = ?", (user_id,))
        conn.commit()

    def get_user_sessions(self, user_id: str, source: str = "webchat",
                          limit: int = 100, project_id: str = None) -> list:
        """ดึง sessions ของ user คนนี้เท่านั้น"""
        conn  = self._conn()
        rows  = conn.execute("""
            SELECT s.id, s.user_id, s.source, s.created_at, s.updated_at, s.title,
                   COUNT(m.id) as msg_count,
                   MAX(CASE WHEN m.role='user' THEN m.content END) as last_user_msg
            FROM sessions s
            LEFT JOIN messages m ON s.id = m.session_id
            WHERE s.user_id = ? AND s.source = ?
              AND (? IS NULL OR s.project_id = ?)
            GROUP BY s.id
            ORDER BY s.updated_at DESC LIMIT ?
        """, (user_id, source, project_id, project_id, limit)).fetchall()
        return [dict(r) for r in rows]

    def stats(self) -> Dict:
        conn = self._conn()
        users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] if self._table_exists("users") else 0
        active_users = conn.execute("SELECT COUNT(*) FROM users WHERE is_active = 1").fetchone()[0] if self._table_exists("users") else 0
        sessions = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        messages = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        memories = conn.execute("SELECT COUNT(*) FROM user_memories").fetchone()[0]
        vectors = conn.execute("SELECT COUNT(*) FROM document_vectors").fetchone()[0] if self._table_exists("document_vectors") else 0
        return {
            "users": users,
            "active_users": active_users,
            "sessions": sessions,
            "messages": messages,
            "memories": memories,
            "document_vectors": vectors,
        }

    def _table_exists(self, table: str) -> bool:
        row = self._conn().execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?",
            (table,)
        ).fetchone()
        return row is not None

    def export_snapshot(self, limit: int = 5000) -> Dict:
        conn = self._conn()
        payload = {"exported_at": datetime.now().isoformat(), "tables": {}}
        for table in ("users", "sessions", "messages", "user_memories", "document_vectors"):
            if not self._table_exists(table):
                payload["tables"][table] = []
                continue
            rows = conn.execute(f"SELECT * FROM {table} LIMIT ?", (limit,)).fetchall()
            payload["tables"][table] = [{k: v for k, v in dict(r).items() if k != "password"} for r in rows]
        return payload


    # ── File Library ──────────────────────────────────────────────────────
    def save_file_meta(self, user_id: str, filename: str, file_hash: str,
                      file_type: str, summary: str = "", project_id: str = None,
                      content_preview: str = ""):
        now = datetime.now().isoformat()
        conn = self._conn()
        conn.execute("""
            INSERT INTO user_files (user_id, filename, file_hash, file_type, file_summary, created_at, project_id, content_preview)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, file_hash) DO UPDATE SET
                filename = excluded.filename,
                project_id = COALESCE(excluded.project_id, user_files.project_id),
                content_preview = CASE WHEN excluded.content_preview != '' THEN excluded.content_preview ELSE user_files.content_preview END,
                file_summary = CASE WHEN excluded.file_summary != '' THEN excluded.file_summary ELSE user_files.file_summary END
        """, (user_id, filename, file_hash, file_type, summary, now, project_id, content_preview[:4000]))
        conn.commit()

    def get_user_files(self, user_id: str, project_id: str = None) -> List[Dict]:
        conn = self._conn()
        if project_id:
            rows = conn.execute("""
                SELECT * FROM user_files WHERE user_id = ? AND project_id = ? ORDER BY created_at DESC
            """, (user_id, project_id)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM user_files WHERE user_id = ? ORDER BY created_at DESC
            """, (user_id,)).fetchall()
        return [dict(r) for r in rows]

    def delete_file(self, user_id: str, file_hash: str):
        conn = self._conn()
        conn.execute("DELETE FROM user_files WHERE user_id = ? AND file_hash = ?", (user_id, file_hash))
        if self._table_exists("document_vectors"):
            conn.execute("DELETE FROM document_vectors WHERE user_id = ? AND file_hash = ?", (user_id, file_hash))
        conn.commit()

# Singleton
db = Database()
