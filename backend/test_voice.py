"""
Quick test script to verify voice server works
Run this AFTER restarting the voice server
"""
import requests
import json

print("=" * 60)
print("VOICE SERVER TEST")
print("=" * 60)

# Test 1: Check voice server is running
print("\n1. Testing voice server (port 8003)...")
try:
    response = requests.get("http://localhost:8003", timeout=5)
    if response.status_code == 200:
        print("   ✅ Voice server is running")
        # Check if the fix is applied
        if '`🎤 Hearing:' in response.text:
            print("   ✅ JavaScript fix is applied (backticks present)")
        else:
            print("   ❌ JavaScript fix NOT applied - need to restart server")
    else:
        print(f"   ❌ Voice server returned status {response.status_code}")
except Exception as e:
    print(f"   ❌ Voice server error: {e}")

# Test 2: Check Ollama
print("\n2. Testing Ollama (port 11434)...")
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code == 200:
        data = response.json()
        models = [m['name'] for m in data.get('models', [])]
        print(f"   ✅ Ollama is running")
        print(f"   Models available: {models}")
        if 'llama3.1:8b' in models:
            print("   ✅ llama3.1:8b model found")
        else:
            print("   ⚠️  llama3.1:8b model NOT found - need to pull it")
    else:
        print(f"   ❌ Ollama returned status {response.status_code}")
except Exception as e:
    print(f"   ❌ Ollama error: {e}")

# Test 3: Check backend API
print("\n3. Testing backend API (port 8000)...")
try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    if response.status_code == 200:
        print("   ✅ Backend API is running")
    else:
        print(f"   ❌ Backend API returned status {response.status_code}")
except Exception as e:
    print(f"   ❌ Backend API error: {e}")

print("\n" + "=" * 60)
print("VOICE SERVER RESTART INSTRUCTIONS")
print("=" * 60)
print("""
To apply the JavaScript fix:

1. Find the terminal running: python voice/voice_server.py
2. Press Ctrl+C to stop it
3. Run again: python voice/voice_server.py
4. Go to http://localhost:8003
5. Click "Start Call" button
6. Allow microphone permission
7. Speak: "Hello" or "I need an appointment"

""")
print("=" * 60)
