
import sys
import os

print("🔍 Verifying Audio Pipeline Dependencies...")

# 1. Check Faster Whisper
try:
    from faster_whisper import WhisperModel
    print("✅ faster-whisper imported successfully.")
except ImportError as e:
    print(f"❌ faster-whisper NOT found: {e}")

# 2. Check Piper TTS
# Piper is often run as a binary, but let's check if we can invoke it or find it.
import subprocess
try:
    result = subprocess.run(["which", "espeak-ng"], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ espeak-ng found at: {result.stdout.strip()}")
    else:
        print("❌ espeak-ng NOT found.")
except Exception as e:
     print(f"❌ Error checking espeak-ng: {e}")

# 3. Check FFmpeg
try:
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ FFmpeg found.")
    else:
        print("❌ FFmpeg NOT found.")
except Exception as e:
     print(f"❌ Error checking FFmpeg: {e}")

print("🏁 Verification Complete.")
