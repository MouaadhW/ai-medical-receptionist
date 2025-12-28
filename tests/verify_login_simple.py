import requests

API_URL = "http://localhost:8000"

def verify_doctor_login():
    print("1. Attempting Login as 'dr_pref_test'...")
    try:
        # Form Data is required for OAuth2
        payload = {
            "username": "dr_pref_test",
            "password": "doctorpassword"
        }
        resp = requests.post(f"{API_URL}/api/auth/login", data=payload)
        
        if resp.status_code == 200:
            print("LOGIN SUCCESS!")
            token = resp.json().get("access_token")
            role = resp.json().get("role")
            print(f"Token received. Role: {role}")
            
            if role == "doctor":
                print("Role verification PASSED.")
                
                # Check Dashboard Access
                print("2. Checking Doctor Dashboard API...")
                headers = {"Authorization": f"Bearer {token}"}
                schedule_resp = requests.get(f"{API_URL}/api/doctor/my-schedule", headers=headers)
                
                if schedule_resp.status_code == 200:
                    print(f"Dashboard Access SUCCESS! Found {len(schedule_resp.json())} appointments.")
                else:
                    print(f"Dashboard Access FAILED: {schedule_resp.status_code} - {schedule_resp.text}")
            else:
                print(f"Role verification FAILED. Expected 'doctor', got '{role}'")
        else:
            print(f"LOGIN FAILED: {resp.status_code} - {resp.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_doctor_login()
