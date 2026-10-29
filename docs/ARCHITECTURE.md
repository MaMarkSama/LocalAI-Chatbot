# Gemma AI architecture

## Directory layout

```text
final_package/
├── gemma_app/              # shared configuration and new core services
├── tests/                  # regression tests (temporary SQLite only)
├── docs/                   # architecture and operational notes
├── data/                   # runtime SQLite + local secret (ignored)
├── backups/                # admin-created backups (ignored)
├── logs/                   # runtime logs (ignored)
├── build_system/           # packaging scripts and generated output
├── webchat.py              # FastAPI web entry point
├── linechat.py             # LINE webhook entry point
├── admin_ui.html           # admin dashboard
└── webchat_ui.html         # user chat UI
```

The root modules remain as compatibility entry points. New cross-cutting code
belongs under `gemma_app/`; future refactors can move one service at a time
without breaking the launcher or installer.

## Request flow

1. `gemma_app.config` loads `.env` and resolves absolute runtime paths.
2. Authentication maps each request to a real user or a signed guest owner.
3. The smart router selects chat, private-library retrieval, or web research.
4. Web research plans multiple queries, deduplicates and ranks results, safely
   extracts public pages, and injects numbered source context.
5. Ollama streams the answer. Sources are appended to persisted messages so
   history and exports retain working references.
6. An immutable `usage_events` row records tokens, model, source, duration and
   tool flags. Existing message token data remains part of reports.

## Scaling notes

SQLite WAL, a 30-second busy timeout and short transactions are suitable for a
single-node small/medium deployment. For multiple application instances or
high write concurrency, move users/sessions/messages/usage events to PostgreSQL
and use Redis for shared rate limits and background jobs. Keep the service/API
boundaries introduced here so that migration does not affect the UI.

## Security boundaries

- Session tokens are stored as keyed hashes, never returned to browser JavaScript.
- A configured `JWT_SECRET` is preferred; development creates a persistent local
  secret under `data/` instead of invalidating every login on restart.
- Web extraction rejects local/private addresses and limits redirects, response
  bytes, source count and context size.
- Web text is explicitly marked untrusted before it reaches the model.
- Admin endpoints require the `admin` role and prevent self-demotion/deactivation.

