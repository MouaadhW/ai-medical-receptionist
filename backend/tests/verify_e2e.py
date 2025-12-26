
import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Verifier")

SERVER_URL = "ws://localhost:8003/ws"

async def verify_e2e():
    logger.info(f"Connecting to {SERVER_URL}...")
    try:
        async with websockets.connect(SERVER_URL) as websocket:
            logger.info("✅ Connected to WebSocket")
            
            # 1. Wait for Greeting
            logger.info("⏳ Waiting for Greeting...")
            try:
                # Greeting might take a moment due to model load
                 while True:
                     greeting_msg = await asyncio.wait_for(websocket.recv(), timeout=120.0) 
                     if isinstance(greeting_msg, bytes):
                         logger.info(f"Received Greeting Audio: {len(greeting_msg)} bytes")
                         continue
                     break
                     
                 # Often initial message is just status, wait for type='speech' or similar
                 # Inspect message
                 logger.info(f"Received: {greeting_msg}")
                 
                 data = json.loads(greeting_msg)
                 if "Welcome" in str(data) or "Hello" in str(data) or data.get("type") == "response": # Adjust based on actual JSON
                     logger.info("✅ Greeting Validated")
                 else:
                     logger.warning("⚠️ Initial message might not be greeting, checking next...")
                     # If the first message isn't the greeting, wait for one more
                     greeting_msg = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                     logger.info(f"Received 2nd: {greeting_msg}")
                     
            except asyncio.TimeoutError:
                logger.error("❌ Timeout waiting for greeting")
                return

            # 2. Send Emergency Message
            logger.info("📤 Sending Emergency Message: 'I have a fever of 104'")
            msg = {
                "type": "speech",
                "text": "I have a fever of 104",
                "confidence": 1.0
            }
            await websocket.send(json.dumps(msg))
            
            # 3. Wait for Response
            logger.info("⏳ Waiting for Triage Response...")
            try:
                start_time = asyncio.get_event_loop().time()
                while True:
                     if asyncio.get_event_loop().time() - start_time > 120:
                         logger.error("❌ Timeout waiting for Triage Response")
                         break
                         
                     response_msg = await asyncio.wait_for(websocket.recv(), timeout=120.0)
                     
                     if isinstance(response_msg, bytes):
                         logger.info(f"Received Audio Bytes: {len(response_msg)} bytes (TTS Generated)")
                         continue # Skip audio for logic check
                         
                     logger.info(f"Received: {response_msg}")
                     
                     data = json.loads(response_msg)
                     text_content = data.get("text", "") or data.get("spoken_response", "")
                     
                     if "emergency" in text_content.lower() or "hospital" in text_content.lower() or "911" in text_content.lower():
                          logger.info("✅ Emergency Response Validated")
                          break
            except asyncio.TimeoutError:
                logger.error("❌ Timeout waiting for response")

    except Exception as e:
        logger.error(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_e2e())
