#!/bin/bash
set -e

echo "=========================================="
echo " AI MEDICAL RECEPTIONIST SYSTEM"
echo "=========================================="
echo ""

echo "[1/6] Checking Ollama..."

if ! command -v ollama &> /dev/null; then
  echo "⚠️ Ollama not found — installing..."

  curl -fsSL https://ollama.com/install.sh | sh

  echo "✅ Ollama installed"
else
  echo "✅ Ollama already installed"
fi

echo "[2/6] Starting Ollama server..."
ollama serve > /tmp/ollama.log 2>&1 &
sleep 5

echo "[3/6] Starting services (Background)..."
# Use PORT from Railway if set, else default to 8000
export APIPORT=${PORT:-8000}

# Move to backend directory so imports and paths work
cd backend
python db/init_db.py

python main.py &
python voice/voice_server.py &

echo "[4/6] Pulling LLM model (Background)..."
# Pull in background so we don't block startup
ollama pull llama3.2:3b &

echo "[5/6] Services Started!"
echo "Server running on port $APIPORT"
echo "Model download continuing in background..."

echo "=========================================="
wait
