import requests
import asyncio
import websockets
import json
import time

# config
API_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8003/ws/chat"

# 1. Setup Data
def setup_doctor_and_user():
    # Login Admin
    print("Logging in Admin...")
    # Using form data
    resp = requests.post(f"{API_URL}/api/auth/login", data={"username": "admin_test", "password": "password123"})
    if resp.status_code != 200:
        # Try creating admin if not exists (unlikely given history) or just fail
        print(f"Admin login failed: {resp.status_code} - {resp.text}")
        return None, None
    
    admin_token = resp.json()["access_token"]
    
    # Create Doctor
    doc_username = "dr_pref_test"
    print(f"Creating Doctor {doc_username}...")
    headers = {"Authorization": f"Bearer {admin_token}"}
    doc_data = {
        "name": "Dr. Preference",
        "username": doc_username,
        "email": "dr_pref@test.com",
        "password": "doctorpassword",
        "specialty": "Cardiology",
        "phone": "555-0101"
    }
    
    # Check if exists first to avoid error
    try:
        resp = requests.post(f"{API_URL}/api/admin/create-doctor", json=doc_data, headers=headers)
        if resp.status_code == 200:
            print("Doctor created.")
        else:
            print(f"Doctor creation status: {resp.status_code} (might already exist)")
    except Exception as e:
        print(f"Error creating doctor: {e}")

    # Login as Patient (using existing test user if possible, or create one)
    user_token = get_user_token()
    return doc_username, user_token

def get_user_token():
    # Login as regular user (Form Data)
    resp = requests.post(f"{API_URL}/api/auth/login", data={"username": "testuser", "password": "testpassword"})
    if resp.status_code == 200:
        return resp.json()["access_token"]
    else:
        # Create
        requests.post(f"{API_URL}/api/auth/register", json={"username": "testuser", "email": "test@test.com", "password": "testpassword"})
        resp = requests.post(f"{API_URL}/api/auth/login", data={"username": "testuser", "password": "testpassword"})
        return resp.json().get("access_token")

async def test_chat_flow(token):
    uri = f"{WS_URL}?token={token}"
    print(f"Connecting to WS: {uri}")
    try:
        async with websockets.connect(uri) as websocket:
            # 1. Initial Greeting
            greeting = await websocket.recv()
            print(f"Agent: {json.loads(greeting)['text']}")
            
            # 2. Send Name/OTID if asked (Auto-verify might skip this)
            if "OTID" in json.loads(greeting)['text']:
                print("Sending Identity...")
                await websocket.send(json.dumps({"text": "Test User 12345"})) # Mock
                resp = await websocket.recv()
                print(f"Agent: {json.loads(resp)['text']}")
            
            # 3. Send Reason
            print("Sending Reason: Chest pain")
            await websocket.send(json.dumps({"text": "I have mild chest pain"})) # Implies Cardiology
            
            resp = await websocket.recv()
            msg = json.loads(resp)
            print(f"Agent: {msg['text']}")
            
            if "doctor" in msg['text'].lower():
                print("Agent asked for doctor preference correctly.")
                
                # 4. Request Specific Doctor
                print("Sending: Dr. Preference")
                await websocket.send(json.dumps({"text": "I want to see Dr. Preference"}))
                
                resp = await websocket.recv()
                msg = json.loads(resp)
                print(f"Agent: {msg['text']}")
                
                if "Dr. Preference" in msg['text']:
                    print("SUCCESS: Agent found Dr. Preference and offered slots.")
                    
                    # 5. Book
                    print("Booking first slot...")
                    await websocket.send(json.dumps({"text": "The first one"}))
                    resp = await websocket.recv()
                    print(f"Agent: {json.loads(resp)['text']}")
                else:
                    print("FAILURE: Agent did not acknowledge Dr. Preference.")
            else:
                print("FAILURE: Agent did not ask for doctor preference.")

    except Exception as e:
        print(f"WS Error: {e}")

def check_doctor_dashboard(doc_username):
    print("Checking Doctor Dashboard...")
    # Login as Doctor (Form Data)
    resp = requests.post(f"{API_URL}/api/auth/login", data={"username": doc_username, "password": "doctorpassword"})
    if resp.status_code != 200:
        print("Doctor login failed")
        return
    
    token = resp.json()["access_token"]
    
    # Get Schedule
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{API_URL}/api/doctor/my-schedule", headers=headers)
    
    if resp.status_code == 200:
        print(f"Doctor Schedule: {resp.json()}")
        if len(resp.json()) > 0:
             print("SUCCESS: Appointment found on Doctor Dashboard.")
        else:
             print("WARNING: No appointments found (maybe booking failed or date is future).")
    else:
        print(f"Error fetching schedule: {resp.status_code}")

if __name__ == "__main__":
    doc_user, user_tok = setup_doctor_and_user()
    if doc_user and user_tok:
        asyncio.get_event_loop().run_until_complete(test_chat_flow(user_tok))
        time.sleep(2)
        check_doctor_dashboard(doc_user)
