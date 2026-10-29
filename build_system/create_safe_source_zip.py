# -*- coding: utf-8 -*-
import fnmatch
import zipfile
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "build_system" / "dist" / "GemmaAI_source_safe.zip"

EXCLUDE = {
    ".env",
    ".wizard_config.json",
    "chat_history.db",
    "chat_history.db-shm",
    "chat_history.db-wal",
}
EXCLUDE_PATTERNS = {
    "__pycache__/*",
    "*.pyc",
    "data/*",
    "backups/*",
    "logs/*",
    "build_system/dist/*",
    "build_system/build_tmp/*",
    "build_system/bundle.zip",
    "build_system/*.spec",
    "build_system/version_info.txt",
    "build_system/setup_wizard_bundled.py",
}


def should_skip(path: Path) -> bool:
    rel = path.relative_to(BASE).as_posix()
    if path.name in EXCLUDE:
        return True
    return any(fnmatch.fnmatch(rel, pattern) for pattern in EXCLUDE_PATTERNS)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in BASE.rglob("*"):
            if path.is_dir() or should_skip(path):
                continue
            zf.write(path, path.relative_to(BASE).as_posix())
    print(f"Created {OUT}")


if __name__ == "__main__":
    main()
