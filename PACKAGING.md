# Packaging Safety

Before sharing or rebuilding a release, do not include local secrets or user data.

## Company release checklist

Use the safe release builder for every external handoff:

```bat
build_system\safe_release.bat
```

The generated zip excludes `.env`, SQLite databases, cache folders, backups, build temp folders, logs, and Python bytecode. Admin users can also trigger the same flow from `POST /api/admin/safe-release`.

Share these:
- Source files
- `.env.example`
- `requirements.txt`
- `README.md`
- Built installer/release artifacts created by `build_system/build.py`

Do not share these:
- `.env`
- `.env.*` except `.env.example`
- `data/` (SQLite database and local session secret)
- `backups/`
- `logs/`
- `.wizard_config.json`
- `__pycache__/`

Create a real environment file only on the target machine:

```bat
copy .env.example .env
```

To create a source zip that is safe to share:

```bat
build_system\create_safe_source_zip.bat
```

If `.env` was already shared, rotate the LINE channel token and secret before using the app again.
