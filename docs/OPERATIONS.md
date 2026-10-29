# Operations

## Run and verify

```powershell
python -m pip install -r requirements.txt
python -m pytest
python webchat.py
```

Open `/` for chat and `/admin` for the administrator dashboard. The dashboard
supports 7/30/90-day Token views, model/source breakdowns, Search health, user
role/status management, security status and recent audit events.

## Runtime data

- SQLite: `data/chat_history.db`
- Backups: `backups/`
- Local fallback session secret: `data/.session_secret`

These paths are excluded from source/release archives. The setup wizard keeps
`data/` and `backups/` when the user chooses to preserve application data.

## Search tuning

The main controls are `SEARCH_MAX_QUERIES`, `SEARCH_MAX_RESULTS`,
`SEARCH_FETCH_PAGES`, `SEARCH_MAX_CONTEXT_CHARS` and `SEARCH_QUERY_PLANNER`.
Reducing query/page counts lowers latency; increasing them improves coverage but
uses more network time and context tokens.

