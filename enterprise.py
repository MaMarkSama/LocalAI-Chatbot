# -*- coding: utf-8 -*-
import json
import os
import platform
import sqlite3
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import httpx

from database import db
from gemma_app.config import BACKUP_DIR, BASE_DIR, DB_PATH as APP_DB_PATH


DB_PATH = APP_DB_PATH

PROMPT_PRESETS = {
    "general": {
        "label": "General Assistant",
        "prompt": "Answer clearly, concisely, and ask for missing context when needed.",
    },
    "document": {
        "label": "Document Analyst",
        "prompt": "Prioritize grounded analysis from the provided document context. State limitations clearly.",
    },
    "coding": {
        "label": "Senior Coding Assistant",
        "prompt": "Focus on correctness, maintainability, tests, and concrete implementation details.",
    },
    "thai_business": {
        "label": "Thai Business",
        "prompt": "ตอบภาษาไทยแบบมืออาชีพ กระชับ ชัดเจน เหมาะกับงานบริษัท",
    },
}


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def init_enterprise_schema() -> None:
    conn = db._conn()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            actor_user_id TEXT,
            actor_role TEXT,
            action TEXT NOT NULL,
            target_type TEXT,
            target_id TEXT,
            ip TEXT,
            user_agent TEXT,
            metadata TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_events(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_audit_actor ON audit_events(actor_user_id, created_at DESC);

        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(user_id, name)
        );
        CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id, updated_at DESC);

        CREATE TABLE IF NOT EXISTS project_documents (
            project_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            file_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY(project_id, user_id, file_hash)
        );
        """
    )
    for ddl in (
        "ALTER TABLE sessions ADD COLUMN project_id TEXT",
        "ALTER TABLE user_memories ADD COLUMN project_id TEXT",
        "ALTER TABLE user_files ADD COLUMN project_id TEXT",
        "ALTER TABLE user_files ADD COLUMN content_preview TEXT",
    ):
        try:
            conn.execute(ddl)
        except Exception:
            pass
    conn.commit()


def audit_event(
    action: str,
    actor: Optional[Dict] = None,
    target_type: str = "",
    target_id: str = "",
    ip: str = "",
    user_agent: str = "",
    metadata: Optional[Dict] = None,
) -> None:
    try:
        conn = db._conn()
        conn.execute(
            """
            INSERT INTO audit_events
            (created_at, actor_user_id, actor_role, action, target_type, target_id, ip, user_agent, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                _now(),
                actor.get("id") if actor else None,
                actor.get("role") if actor else None,
                action,
                target_type,
                target_id,
                ip,
                user_agent,
                json.dumps(metadata or {}, ensure_ascii=False),
            ),
        )
        conn.commit()
    except Exception:
        pass


def list_audit_events(limit: int = 200, actor_user_id: str = "", action: str = "") -> List[Dict]:
    conn = db._conn()
    query = "SELECT * FROM audit_events WHERE 1=1"
    args: List = []
    if actor_user_id:
        query += " AND actor_user_id = ?"
        args.append(actor_user_id)
    if action:
        query += " AND action = ?"
        args.append(action)
    query += " ORDER BY id DESC LIMIT ?"
    args.append(max(1, min(int(limit), 1000)))
    rows = conn.execute(query, args).fetchall()
    return [dict(r) for r in rows]


def security_dashboard() -> Dict:
    conn = db._conn()
    stats = db.stats()
    token_rows = conn.execute(
        """
        SELECT COUNT(*) AS total,
               SUM(CASE WHEN expires_at > ? THEN 1 ELSE 0 END) AS active
        FROM user_tokens
        """,
        (_now(),),
    ).fetchone() if db._table_exists("user_tokens") else {"total": 0, "active": 0}
    failed_rows = conn.execute(
        "SELECT username, attempts, locked_until, updated_at FROM login_attempts ORDER BY updated_at DESC LIMIT 20"
    ).fetchall() if db._table_exists("login_attempts") else []
    recent_audit = list_audit_events(limit=30)
    return {
        "stats": stats,
        "tokens": {"total": token_rows["total"] or 0, "active": token_rows["active"] or 0},
        "failed_logins": [dict(r) for r in failed_rows],
        "recent_audit": recent_audit,
    }


async def validate_runtime(ollama_base_url: str, model: str, web_port: int) -> Dict:
    checks = {
        "python": {"ok": True, "version": platform.python_version()},
        "database": {"ok": DB_PATH.exists(), "path": str(DB_PATH)},
        "secrets": {
            "ok": bool(os.getenv("JWT_SECRET")) and os.getenv("JWT_SECRET") != "local-dev-secret",
            "has_line_token": bool(os.getenv("LINE_CHANNEL_ACCESS_TOKEN")),
            "has_line_secret": bool(os.getenv("LINE_CHANNEL_SECRET")),
        },
        "ollama": {"ok": False, "model_loaded": False, "base_url": ollama_base_url},
        "ports": {"web_port": web_port},
    }
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{ollama_base_url}/api/tags")
            r.raise_for_status()
            models = [m.get("name", "") for m in r.json().get("models", [])]
            checks["ollama"] = {
                "ok": True,
                "model_loaded": any(model in m for m in models),
                "models": models,
                "base_url": ollama_base_url,
            }
    except Exception as e:
        checks["ollama"]["error"] = str(e)
    checks["ok"] = all(
        value.get("ok", True)
        for value in checks.values()
        if isinstance(value, dict)
    )
    return checks


def create_project(user_id: str, name: str, description: str = "") -> Dict:
    import secrets

    name = (name or "").strip()
    if len(name) < 2:
        return {"ok": False, "error": "Project name is too short"}
    project_id = secrets.token_hex(8)
    now = _now()
    conn = db._conn()
    try:
        conn.execute(
            """
            INSERT INTO projects (id, user_id, name, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (project_id, user_id, name, description.strip(), now, now),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return {"ok": False, "error": "Project name already exists"}
    return {"ok": True, "project": get_project(user_id, project_id)}


def list_projects(user_id: str) -> List[Dict]:
    rows = db._conn().execute(
        "SELECT * FROM projects WHERE user_id = ? ORDER BY updated_at DESC",
        (user_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def get_project(user_id: str, project_id: str) -> Optional[Dict]:
    row = db._conn().execute(
        "SELECT * FROM projects WHERE id = ? AND user_id = ?",
        (project_id, user_id),
    ).fetchone()
    return dict(row) if row else None


def update_session_project(user_id: str, session_id: str, project_id: str = "") -> Dict:
    if project_id and not get_project(user_id, project_id):
        return {"ok": False, "error": "Project not found"}
    conn = db._conn()
    conn.execute(
        "UPDATE sessions SET project_id = ? WHERE id = ? AND user_id = ?",
        (project_id or None, session_id, user_id),
    )
    conn.commit()
    return {"ok": True}


def export_chat_markdown(session_id: str) -> str:
    session = db.get_session(session_id) or {}
    messages = db.get_session_messages(session_id)
    title = session.get("title") or session_id
    lines = [f"# {title}", "", f"- Session: `{session_id}`", f"- Exported: {_now()}", ""]
    for msg in messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        lines.extend([f"## {role}", "", msg["content"], ""])
    return "\n".join(lines)


def create_backup() -> Dict:
    backup_dir = BACKUP_DIR
    backup_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = backup_dir / f"backup_{stamp}.zip"
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        if DB_PATH.exists():
            zf.write(DB_PATH, DB_PATH.name)
        for suffix in ("-wal", "-shm"):
            p = Path(str(DB_PATH) + suffix)
            if p.exists():
                zf.write(p, p.name)
        manifest = {
            "created_at": _now(),
            "app": "Local-Ai-Chatbot",
            "contains": ["sqlite"],
        }
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return {"ok": True, "path": str(dest), "size": dest.stat().st_size}


def safe_release_zip(output: Optional[str] = None) -> Dict:
    output_path = Path(output) if output else BASE_DIR / "build_system" / "safe_release.zip"
    if not output_path.is_absolute():
        output_path = BASE_DIR / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    blocked_names = {
        ".env", ".session_secret", ".wizard_config.json",
        "chat_history.db", "chat_history.db-wal", "chat_history.db-shm",
        "safe_release.zip", "bundle.zip",
    }
    blocked_dirs = {"__pycache__", "backups", "data", "logs", "build_tmp", "dist", ".git", ".pytest_cache", ".ruff_cache", ".venv", "venv"}
    blocked_suffixes = {".pyc", ".pyo", ".sqlite", ".sqlite3", ".log", ".key", ".pem"}
    included = 0
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in BASE_DIR.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(BASE_DIR)
            parts = set(rel.parts)
            if (
                path.name in blocked_names
                or (path.name.startswith(".env.") and path.name != ".env.example")
                or parts & blocked_dirs
                or path.suffix.lower() in blocked_suffixes
            ):
                continue
            try:
                if rel == output_path.relative_to(BASE_DIR):
                    continue
            except ValueError:
                pass
            zf.write(path, rel.as_posix())
            included += 1
        zf.writestr(
            "RELEASE_MANIFEST.json",
            json.dumps({"created_at": _now(), "included_files": included}, ensure_ascii=False, indent=2),
        )
    return {"ok": True, "path": str(output_path), "included_files": included, "size": output_path.stat().st_size}


def revoke_user_tokens(user_id: str) -> int:
    conn = db._conn()
    cur = conn.execute("DELETE FROM user_tokens WHERE user_id = ?", (user_id,))
    conn.commit()
    return cur.rowcount


try:
    init_enterprise_schema()
except sqlite3.OperationalError:
    # The app may be imported in read-only packaging or test contexts.
    # Write endpoints will surface database errors when they are actually used.
    pass
