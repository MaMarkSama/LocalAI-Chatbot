#!/usr/bin/env bash
set -e

echo ""
echo "======================================================"
echo "  Gemma AI — Docker Portable Launcher (Linux / macOS)"
echo "======================================================"
echo ""

# Navigate to script directory
cd "$(dirname "$0")"

# 1. Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Error: Docker daemon is not running. Please start Docker service."
    exit 1
fi

# 2. Load pre-built tar image if present
if [ -f "gemma-ai-chatbot-image.tar" ]; then
    echo "📦 Found pre-built image archive. Loading image into Docker..."
    docker load -i gemma-ai-chatbot-image.tar
    echo "✅ Image loaded successfully!"
    echo ""
fi

# 3. Create .env from template if missing
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "⚙️ Creating default .env configuration..."
    cp .env.example .env
fi

# 4. Start via docker compose
echo "🚀 Starting Gemma AI container..."
docker compose up -d

echo ""
echo "======================================================"
echo "  ✅ Gemma AI is running successfully!"
echo "  URL: http://localhost:8001"
echo "  Admin: http://localhost:8001/admin"
echo "======================================================"
echo ""

# Attempt to open browser
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8001 &
elif command -v open &> /dev/null; then
    open http://localhost:8001 &
fi
