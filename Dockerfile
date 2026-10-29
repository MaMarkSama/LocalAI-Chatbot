# ==============================================================================
# Gemma AI — Enterprise Local AI Assistant
# Production-ready Container Image for Portable Deployment
# ==============================================================================

FROM python:3.11-slim

# Prevent Python from writing bytecode and enable immediate stdout flushing
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

WORKDIR /app

# Install system dependencies (curl for healthcheck, ca-certificates)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code and web templates
COPY webchat.py linechat.py smart_router.py security.py database.py \
     user_manager.py usage_tracker.py web_searcher.py file_processor.py \
     message_turbovec.py memory_manager.py conversation.py auth_middleware.py \
     enterprise.py ./
COPY webchat_ui.html admin_ui.html ./
COPY gemma_app/ ./gemma_app/
COPY skill/ ./skill/
COPY tokens/ ./tokens/
COPY .env.example ./.env.example

# Create storage directories and set non-root permissions for enterprise security
RUN mkdir -p /app/data /app/logs /app/backups && \
    useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose Web Chat port (8001) and LINE Bot Webhook port (8000)
EXPOSE 8001 8000

# Built-in container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8001/ || exit 1

# Default entrypoint: Start FastAPI Web Chat server
CMD ["uvicorn", "webchat:app", "--host", "0.0.0.0", "--port", "8001"]
