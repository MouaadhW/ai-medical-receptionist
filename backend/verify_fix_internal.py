import asyncio
import websockets
import json
import requests
import sys
import os

# Internal Configuration
API_URL = "http://medical_backend:8000"
WS_URL = "ws://localhost:8003/ws"
USERNAME = "jetski_test_final"
PASSWORD = "SecurePassword123!"

async def verify_fix():
    print(f"1. logging in as {USERNAME} to {API_URL}...")
    try:
        # Using correct endpoint /api/auth/login with form data
        response = requests.post(f"{API_URL}/api/auth/login", data={"username": USERNAME, "password": PASSWORD})
        response.raise_for_status()
        token = response.json()["access_token"]
        print("   Success! Token received.")
    except Exception as e:
        print(f"   Failed to login: {e}")
        return

    print(f"2. Connecting to WebSocket with token...")
    uri = f"{WS_URL}?token={token}"
    
    async with websockets.connect(uri) as websocket:
        print("   Connected!")
        
        # Wait for greeting
        greeting = await websocket.recv()
        print(f"   Received: {json.loads(greeting)['text'] if 'text' in json.loads(greeting) else 'Audio/Binary'}")
        
        # Step 3: Send "Book appointment"
        print("3. Sending 'Book appointment'...")
        await asyncio.sleep(2)
        await websocket.send(json.dumps({"type": "speech", "text": "Book appointment"}))
        
        # Expect response (asking for reason, NOT name/otid)
        # We might get audio bytes first, ignore them
        while True:
            resp = await websocket.recv()
            if isinstance(resp, str):
                data = json.loads(resp)
                if data.get("type") == "response":
                    text = data.get("text", "")
                    print(f"   Agent: {text}")
                    if "reason" in text.lower():
                        print("   SUCCESS! Agent asked for reason (skipped verification as expected).")
                        break
                    if "name" in text.lower() or "otid" in text.lower():
                        print("   FAILURE! Agent asked for name/OTID.")
                        return

        # Step 4: Send "Headache"
        print("4. Sending 'Headache'...")
        await asyncio.sleep(2)
        await websocket.send(json.dumps({"type": "speech", "text": "Headache"}))
        
        # Wait for slots
        while True:
            resp = await websocket.recv()
            if isinstance(resp, str):
                data = json.loads(resp)
                if data.get("type") == "response":
                    print(f"   Agent: {data.get('text')}")
                    if "appointments available" in data.get("text", "").lower():
                        break

        # Step 5: Send "First one"
        print("5. Sending 'First one'...")
        await asyncio.sleep(2)
        await websocket.send(json.dumps({"type": "speech", "text": "The first one"}))
        
        # Wait for confirmation
        while True:
            resp = await websocket.recv()
            if isinstance(resp, str):
                data = json.loads(resp)
                if data.get("type") == "response":
                    print(f"   Agent: {data.get('text')}")
                    if "scheduled" in data.get("text", "").lower():
                        print("   Booking Confirmed!")
                        break

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(verify_fix())
    except Exception as e:
        print(f"Test Failed: {e}")
