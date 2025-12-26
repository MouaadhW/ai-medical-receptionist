
import asyncio
import sys
import os
import json
from agent.medical_agent import MedicalReceptionistAgent

async def test_agent_directly():
    print("🤖 Initializing Agent inside Docker...")
    try:
        agent = MedicalReceptionistAgent()
        print("✅ Agent Initialized")
    except Exception as e:
        print(f"❌ Agent Init Failed: {e}")
        return

    print("🏁 Requesting Greeting (processinput)...")
    try:
        # Use a dummy history
        response = await agent.processinput("Hello", [])
        print(f"✅ Response Received: {response}")
    except Exception as e:
        print(f"❌ call to processinput failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_agent_directly())
