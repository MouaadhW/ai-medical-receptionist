import asyncio
import sys
import os
import json

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.medical_agent import MedicalReceptionistAgent

async def test_json_output():
    print("🤖 Initializing Agent...")
    agent = MedicalReceptionistAgent()
    
    # Mock history
    history = []
    
    print("\n🧪 Test 1: General Greeting")
    response_1 = await agent.processinput("Hello", history)
    print(f"Raw Output: {response_1}")
    
    try:
        json_1 = json.loads(response_1)
        print("✅ Valid JSON")
        print(f"Unknown keys: {json_1.keys()}")
        if "spoken_response" in json_1 and "metadata" in json_1:
             print("✅ Structure Correct")
        else:
             print("❌ Structure Invalid")
    except json.JSONDecodeError:
        print("❌ Invalid JSON")

    print("\n🧪 Test 2: Emergency Triage")
    response_2 = await agent.processinput("I have crushing chest pain", history)
    print(f"Raw Output: {response_2}")
    
    try:
        json_2 = json.loads(response_2)
        print("✅ Valid JSON")
        if json_2.get("metadata", {}).get("is_emergency"):
             print("✅ Emergency Detected Correctly")
        else:
             print("❌ Emergency Flag Missing")
    except json.JSONDecodeError:
        print("❌ Invalid JSON")

if __name__ == "__main__":
    asyncio.run(test_json_output())
