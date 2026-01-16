
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import asyncio
import json
import logging
import numpy as np
import webrtcvad
import collections
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from faster_whisper import WhisperModel
import subprocess
import aiohttp

# --- Configuration ---
SAMPLE_RATE = 16000
FRAME_DURATION_MS = 30
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)  # 480 samples for 16kHz
VAD_MODE = 1  # Less Aggressive (0-3) - 3 rejects too much background noise/poor mics - 3 rejects too much background noise/poor mics

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MIMIC_DATA_PATH = os.path.join(BASE_DIR, "mimicdata")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VoiceServer")

# Add backend to path
sys.path.insert(0, BASE_DIR)
from agent.medical_agent import MedicalReceptionistAgent
from db.database import SessionLocal
from db.models import Call, User
import config
from auth import decode_access_token

app = FastAPI(title="Medical Receptionist Streaming Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global Resources ---
agent = MedicalReceptionistAgent()
vad = webrtcvad.Vad(VAD_MODE)
executor = ThreadPoolExecutor(max_workers=3)  # For STT/TTS blocking calls

# Initialize Whisper (Lazy load or startup?)
# using 'base' for multilingual support (en/fr)
logger.info("Loading Whisper Model...")
# Use 'base' for better multilingual performance, or 'tiny' for speed if 'base' is too slow
stt_model = WhisperModel("base", device="cpu", compute_type="int8", download_root=MODELS_DIR)
logger.info("Whisper Model Loaded.")

# Piper Configuration
PIPER_MODELS = {
    "en": "en_US-lessac-medium.onnx",
    "fr": "fr_FR-upmc-medium.onnx"
}

# Base URL for Piper models
PIPER_URL_BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main"

PIPER_MODEL_PATHS = {
    "en": os.path.join(MODELS_DIR, PIPER_MODELS["en"]),
    "fr": os.path.join(MODELS_DIR, PIPER_MODELS["fr"])
}

async def ensure_piper_models():
    """Check if piper models exist, else download them."""
    
    # Model URLs mapping
    urls = {
        "en": f"{PIPER_URL_BASE}/en/en_US/lessac/medium/{PIPER_MODELS['en']}",
        "fr": f"{PIPER_URL_BASE}/fr/fr_FR/upmc/medium/{PIPER_MODELS['fr']}"
    }

    async with aiohttp.ClientSession() as session:
        for lang, model_name in PIPER_MODELS.items():
            model_path = PIPER_MODEL_PATHS[lang]
            json_path = model_path + ".json"
            
            if not os.path.exists(model_path) or not os.path.exists(json_path):
                logger.info(f"Downloading Piper Model ({lang}): {model_name}...")
                url = urls[lang]
                json_url = url + ".json"
                
                # Download ONNX
                async with session.get(url) as resp:
                    if resp.status == 200:
                        with open(model_path, 'wb') as f:
                            f.write(await resp.read())
                    else:
                        logger.error(f"Failed to download model {model_name}: status {resp.status}")
                
                # Download JSON config
                async with session.get(json_url) as resp:
                    if resp.status == 200:
                        with open(json_path, 'wb') as f:
                            f.write(await resp.read())
                
                logger.info(f"Piper Model ({lang}) Downloaded.")

@app.on_event("startup")
async def startup_event():
    await ensure_piper_models()

# --- Audio Processing Helpers ---

def transcribe_audio(audio_float32):
    """Run Whisper transcription on float32 numpy array."""
    # Remove language="en" to allow auto-detection
    segments, info = stt_model.transcribe(audio_float32, beam_size=5, vad_filter=True)
    text = " ".join([segment.text for segment in segments]).strip()
    return text

def run_tts(text, language="en"):
    """Generate audio using Piper TTS (via subprocess). Returns bytes (WAV/PCM)."""
    # Echo text into piper
    # Command: echo "text" | piper --model model_path --output_raw
    
    # Fallback to english if lang not supported
    if language not in PIPER_MODEL_PATHS:
        language = "en"
        
    model_path = PIPER_MODEL_PATHS[language]

    try:
        cmd = [
            "piper",
            "--model", model_path,
            "--output_raw" # Output raw 16-bit 22050Hz (usually) or 16000Hz depending on model
        ]
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(input=text.encode('utf-8'))
        
        if process.returncode != 0:
            logger.error(f"Piper TTS Error: {stderr.decode()}")
            return None
        
        return stdout # Raw PCM bytes
    except Exception as e:
        logger.error(f"TTS Exception: {e}")
        return None

class VADManager:
    """Manages Voice Activity Detection state."""
    def __init__(self):
        self.buffer = collections.deque(maxlen=20) # Keep last ~600ms
        self.triggered = False
        self.speech_frames = []
        self.silence_counter = 0
        self.SILENCE_THRESHOLD = 30 # approx 1 second of silence to stop

    def process_frame(self, frame_bytes):
        is_speech = vad.is_speech(frame_bytes, SAMPLE_RATE)
        
        if not self.triggered:
            if is_speech:
                self.triggered = True
                self.speech_frames.extend(self.buffer)
                self.speech_frames.append(frame_bytes)
                logger.debug("Speech START")
            else:
                self.buffer.append(frame_bytes)
        else:
            self.speech_frames.append(frame_bytes)
            if not is_speech:
                self.silence_counter += 1
            else:
                self.silence_counter = 0
            
            if self.silence_counter > self.SILENCE_THRESHOLD:
                self.triggered = False
                self.silence_counter = 0
                logger.debug("Speech END")
                # Return the full audio buffer for processing
                full_audio = b''.join(self.speech_frames)
                self.speech_frames = []
                self.buffer.clear()
                return full_audio
        
        return None

# --- WebSocket Endpoint ---

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    await websocket.accept()
    logger.info(f"Client Connected. Token present? {bool(token)}")
    if token:
        logger.info(f"Token: {token[:10]}...")
    
    # Authenticate via Token
    user = None
    if token:
        try:
            payload = decode_access_token(token)
            username = payload.get("sub")
            if username:
                db = SessionLocal()
                user = db.query(User).filter(User.username == username).first()
                if user:
                    # Eager load patient
                    _ = user.patient
                db.close()
                logger.info(f"Authenticated User: {username}")
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
    
    # Init Call Record
    try:
        db = SessionLocal()
        call = Call(callernumber="Web Stream", starttime=datetime.now(), status='inprogress')
        db.add(call)
        db.commit()
        call_id = str(call.id)
        db.close()
    except Exception as e:
        logger.error(f"Failed to init DB record: {e}")
        call_id = "temp_" + str(int(time.time()))
    
    # Initialize Conversation State with User Info (if authenticated)
    if user:
        agent.conversationstate[call_id] = {
            "intent": None,
            "patientid": user.patient_id,
            "patientname": user.patient.name if user.patient else user.username,
            "userid": user.id,
            "phone": None,
            "verified": True,   # Auto-verify logged-in users
            "otid": user.otid,
            "awaitingname": False,
            "awaitingkey": False,
            "awaitingreason": False,
            "appointmentreason": None,
            "retrycount": 0
        }
        logger.info(f"State set for call_id '{call_id}': {agent.conversationstate.get(call_id)}")
    else:
        logger.info("User not authenticated or user object is None")

    conversation_history = []
    
    # Initialize VAD Manager for this connection
    vad_manager = VADManager()
    
    try:
        # Send initial greeting
        greeting = agent.getgreeting()
        conversation_history.append({"role": "assistant", "content": greeting})
        
        # TTS Greeting (Async)
        logger.info(f"Generating Greeting: {greeting}")
        audio_bytes = await asyncio.get_event_loop().run_in_executor(executor, run_tts, greeting, "en")
        
        # Send control + audio
        if audio_bytes:
             # Send metadata first
            await websocket.send_text(json.dumps({
                "type": "response", 
                "text": greeting,
                "role": "assistant"
            }))
            # Send Binary Audio
            await websocket.send_bytes(audio_bytes)
            logger.info("Sent Greeting Audio")

        # Construct User Context for State Enforcement
        user_context = None
        if user:
            user_context = {
                "patientid": user.patient_id,
                "patientname": user.patient.name if user.patient else user.username,
                "userid": user.id,
                "verified": True,
                "otid": user.otid,
                "awaitingkey": False
            }

        while True:
            # Expecting either JSON (control) or Binary (audio)
            message = await websocket.receive()
            
            if "bytes" in message:
                audio_chunk = message["bytes"]
                
                # Check frame size compatibility
                # Webrtcvad needs exactly 10, 20, or 30ms frames.
                # 16000Hz * 0.030s = 480 samples * 2 bytes = 960 bytes
                # If chunk is larger, we must split it.
                
                # Log audio energy to debug silence
                if len(audio_chunk) > 0:
                     audio_np_debug = np.frombuffer(audio_chunk, dtype=np.int16)
                     rms = np.sqrt(np.mean(audio_np_debug**2))
                     if rms < 100: # Silence threshold roughly
                         # logger.debug(f"Silence detected (RMS: {rms:.2f})")
                         pass
                     else:
                         logger.info(f"Audio received (Bytes: {len(audio_chunk)}, RMS: {rms:.2f})")

                # Log audio energy to debug silence
                if len(audio_chunk) > 0:
                     audio_np_debug = np.frombuffer(audio_chunk, dtype=np.int16)
                     rms = np.sqrt(np.mean(audio_np_debug**2))
                     if rms < 100: # Silence threshold roughly
                         # logger.debug(f"Silence detected (RMS: {rms:.2f})")
                         pass
                     else:
                         logger.info(f"Audio received (Bytes: {len(audio_chunk)}, RMS: {rms:.2f})")

                offset = 0
                while offset + 960 <= len(audio_chunk):
                    frame = audio_chunk[offset:offset+960]
                    offset += 960
                    
                    speech_audio = vad_manager.process_frame(frame)
                    
                    if speech_audio:
                        logger.info(f"Processing Speech Segment ({len(speech_audio)} bytes)...")
                        
                        # Convert to float32 for Whisper
                        # 1. From Int16 to Float32
                        audio_np = np.frombuffer(speech_audio, dtype=np.int16).astype(np.float32) / 32768.0
                        
                        # 2. Transcribe (Blocking -> Thread)
                        user_text = await asyncio.get_event_loop().run_in_executor(executor, transcribe_audio, audio_np)
                        logger.info(f"User Said: {user_text}")
                        
                        if not user_text.strip():
                            continue
                            
                        # Send transcript update
                        await websocket.send_text(json.dumps({
                            "type": "transcript",
                            "text": user_text,
                            "role": "user"
                        }))
                        
                        # 3. Agent Logic
                        if "goodbye" in user_text.lower():
                            farewell = "Goodbye! Take care."
                            await websocket.send_text(json.dumps({"type": "response", "text": farewell, "endcall": True}))
                            break
                            
                        conversation_history.append({"role": "user", "content": user_text})
                        
                        # Call Agent (Blocking-ish)
                        # The agent.processinput returns a JSON string now
                        print(f"DEBUG_VOICE: Calling processinput with context: {user_context}", flush=True)
                        json_response = await agent.processinput(user_text, conversation_history, callid=call_id, user_context=user_context)
                        
                        try:
                            parsed_response = json.loads(json_response)
                            agent_text = parsed_response.get("spoken_response", "")
                            # Extract language if provided, default to en
                            response_metadata = parsed_response.get("metadata", {})
                            language = response_metadata.get("language", "en")
                        except:
                            agent_text = json_response
                            language = "en"
                        
                        conversation_history.append({"role": "assistant", "content": agent_text})
                        logger.info(f"Agent Response ({language}): {agent_text}")
                        
                        # 4. Generate TTS
                        tts_audio = await asyncio.get_event_loop().run_in_executor(executor, run_tts, agent_text, language)
                        
                        if tts_audio:
                             await websocket.send_text(json.dumps({
                                "type": "response", # triggers client to play next blob
                                "text": agent_text,
                                "role": "assistant"
                            }))
                             await websocket.send_bytes(tts_audio)

            elif "text" in message:
                # Handle control messages (if any)
                data = json.loads(message["text"])
                msg_type = data.get("type")
                
                if msg_type == "start":
                    pass 
                
                elif msg_type == "speech":
                    # Simulated speech for testing/legacy frontend
                    user_text = data.get("text", "")
                    logger.info(f"Simulated Speech: {user_text}")
                    
                    conversation_history.append({"role": "user", "content": user_text})
                    
                    # Call Agent
                    json_response = await agent.processinput(user_text, conversation_history, callid=call_id, user_context=user_context)
                    try:
                        parsed_response = json.loads(json_response)
                        agent_text = parsed_response.get("spoken_response", "")
                        language = parsed_response.get("metadata", {}).get("language", "en")
                    except:
                        agent_text = json_response
                        language = "en"
                    
                    conversation_history.append({"role": "assistant", "content": agent_text})
                    logger.info(f"Agent Response: {agent_text}")
                    
                    # Generate TTS
                    tts_audio = await asyncio.get_event_loop().run_in_executor(executor, run_tts, agent_text, language)
                    
                    if tts_audio:
                         await websocket.send_text(json.dumps({
                            "type": "response", 
                            "text": agent_text,
                            "role": "assistant"
                        }))
                         await websocket.send_bytes(tts_audio)
    
    except WebSocketDisconnect:
        logger.info("Client Disconnected")
    except Exception as e:
        logger.error(f"WS Error: {e}", exc_info=True)
    finally:
        # Save Call Status
        pass

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Streaming Voice Server...")
    uvicorn.run(app, host=config.config.APIHOST, port=config.config.VOICEPORT)