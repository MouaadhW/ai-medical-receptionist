#!/bin/bash
echo "=========================================="
echo " AI MEDICAL RECEPTIONIST SYSTEM"
echo "=========================================="
echo ""
echo "[1/5] Checking Ollama..."
if ! command -v ollama &> /dev/null; then
  echo "ERROR: Ollama not installed!"
  echo "Please install: https://ollama.com/download"
  exit 1
fi
echo "[2/5] Pulling LLM model..."
ollama pull llama3.1:8b
echo "[3/5] Installing dependencies..."
cd backend
pip install -q -r requirements.txt
echo "[4/5] Initializing database..."
python db/init_db.py
echo "[5/5] Starting services..."
python main.py &
sleep 3
python voice/voice_server.py &
echo ""
echo "=========================================="
echo " ✅ SYSTEM READY!"
echo "=========================================="
echo ""
echo "📱 Voice Interface: "
echo "🔌 API Server: "
echo "📊 API Docs: /docs"
echo ""
echo "Test Patients:"
echo " • John Smith (SMITH1985)"
echo " • Mary Johnson (JOHNSON1990)"
echo " • Robert Davis (DAVIS1978)"
echo ""
echo "=========================================="
