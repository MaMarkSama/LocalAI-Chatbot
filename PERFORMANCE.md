# Performance Tuning

Recommended defaults for a smoother local UX:

```env
OLLAMA_NUM_CTX=4096
OLLAMA_MAX_RESPONSE_TOKENS=1536
CONVERSATION_MAX_TURNS=12
OLLAMA_WARMUP_ENABLED=1
MAX_UPLOAD_BYTES=26214400
MAX_TABLE_ROWS=5000
TURBOVEC_CHUNK_CHARS=2000
TURBOVEC_TOP_K=6
SEARCH_MAX_QUERIES=3
SEARCH_MAX_RESULTS=8
SEARCH_FETCH_PAGES=5
SEARCH_CACHE_TTL_SECONDS=300
```

If responses are still slow:
- Use a smaller or more quantized Ollama model.
- Lower `OLLAMA_NUM_CTX` to `2048`.
- Lower `OLLAMA_MAX_RESPONSE_TOKENS` to `768` or `1024`.
- Lower `CONVERSATION_MAX_TURNS` to `8`.

If file analysis is slow:
- Keep `MAX_TABLE_ROWS` near `5000` for Excel/CSV.
- Use `TURBOVEC_ENABLED=1` so repeated file questions can reuse the index.
- Ask narrower questions about large files; broad summaries require more model work.

If web research is slow:
- Lower `SEARCH_MAX_QUERIES` to `1` or `2`.
- Lower `SEARCH_FETCH_PAGES` to `2` or `3`.
- Keep the cache enabled so repeated questions do not repeat network work.

For first-response latency:
- Keep `OLLAMA_WARMUP_ENABLED=1`.
- Start Ollama before opening the web chat.
