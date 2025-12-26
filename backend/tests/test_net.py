
import requests
try:
    print("Testing connection to Ollama...")
    r = requests.get("http://ollama:11434/api/tags")
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Error: {e}")
