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

echo "[3/6] Pulling LLM model..."
ollama pull llama3.1:8b

echo "[4/6] Installing dependencies..."
cd backend
pip install -q -r requirements.txt

echo "[5/6] Initializing database..."
python db/init_db.py

echo "[6/6] Starting services..."
python main.py &

sleep 3
python voice/voice_server.py &

echo ""
echo "=========================================="
echo " ✅ SYSTEM READY!"
echo "=========================================="
