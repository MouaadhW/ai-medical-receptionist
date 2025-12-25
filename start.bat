@echo off
cls
echo.
echo ==========================================
echo AI MEDICAL RECEPTIONIST SYSTEM
echo ==========================================
echo.
echo [1/5] Checking Ollama...
ollama --version >nul 2>&1
if errorlevel 1 (
  echo ERROR: Ollama not installed!
  echo Please install: https://ollama.com/download
  pause
  exit /b 1
)
echo [2/5] Pulling LLM model...
ollama pull llama3.1:8b
echo [3/5] Installing dependencies...
cd backend
pip install -q -r requirements.txt
echo [4/5] Initializing database...
python db/init_db.py
echo [5/5] Starting services...
start "API Server" python main.py
timeout /t 3 >nul
start "Voice Server" python voice/voice_server.py
timeout /t 3 >nul
echo.
echo ==========================================
echo ✅ SYSTEM READY!
echo ==========================================
echo.
echo 📱 Voice Interface:
echo 🔌 API Server:
echo 📊 API Docs: /docs
echo.
echo Test Patients:
echo • John Smith (SMITH1985)
echo • Mary Johnson (JOHNSON1990)
echo • Robert Davis (DAVIS1978)
echo.
echo ==========================================
pause
