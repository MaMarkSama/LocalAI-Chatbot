"""Central application configuration and runtime paths.

This module loads ``.env`` before any service reads environment variables.  It
also resolves every runtime path from the project directory, so launching the
app from a different working directory cannot create a second database.
"""
from __future__ import annotations

import os
import secrets
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _path_from_env(name: str, default: Path) -> Path:
    value = os.getenv(name, "").strip()
    path = Path(value).expanduser() if value else default
    return path if path.is_absolute() else BASE_DIR / path


DATA_DIR = _path_from_env("APP_DATA_DIR", Path("data"))
LOG_DIR = _path_from_env("APP_LOG_DIR", Path("logs"))
BACKUP_DIR = _path_from_env("APP_BACKUP_DIR", Path("backups"))
DB_PATH = _path_from_env("DB_PATH", DATA_DIR / "chat_history.db")

for runtime_dir in {DATA_DIR, LOG_DIR, BACKUP_DIR, DB_PATH.parent}:
    runtime_dir.mkdir(parents=True, exist_ok=True)


def _session_secret() -> str:
    configured = os.getenv("JWT_SECRET", "").strip()
    if configured and configured not in {"local-dev-secret", "change-me", "your-secret-here"}:
        return configured

    # Keep development sessions valid across restarts without putting a secret
    # in source control. Production should always set JWT_SECRET explicitly.
    secret_file = DATA_DIR / ".session_secret"
    try:
        if secret_file.exists():
            saved = secret_file.read_text(encoding="utf-8").strip()
            if len(saved) >= 32:
                return saved
        generated = secrets.token_urlsafe(48)
        secret_file.write_text(generated, encoding="utf-8")
        return generated
    except OSError:
        # Read-only packaged environments still start, but validation will flag
        # the missing configured secret.
        return secrets.token_urlsafe(48)


SESSION_SECRET = _session_secret()


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int, minimum: int | None = None, maximum: int | None = None) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        value = default
    if minimum is not None:
        value = max(minimum, value)
    if maximum is not None:
        value = min(maximum, value)
    return value

