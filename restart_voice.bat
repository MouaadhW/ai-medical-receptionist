@echo off
echo ============================================================
echo RESTARTING VOICE SERVER WITH FIX
echo ============================================================
echo.
echo This will:
echo 1. Stop the old voice server (with JavaScript bug)
echo 2. Start new voice server (with fix applied)
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause > nul

cd backend

echo.
echo Starting voice server on port 8003...
echo.
echo ============================================================
echo VOICE SERVER - PORT 8003
echo ============================================================
echo.
echo After this starts:
echo 1. Open browser to: http://localhost:8003
echo 2. Click "Start Call" button
echo 3. Allow microphone when prompted
echo 4. Speak: "I need an appointment"
echo.
echo Press Ctrl+C to stop when done testing
echo ============================================================
echo.

python voice/voice_server.py
