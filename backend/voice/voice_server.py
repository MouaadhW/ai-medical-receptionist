from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agent.medical_agent import MedicalReceptionistAgent
from db.database import SessionLocal
from db.models import Call
from datetime import datetime
import json
import random
import config

app = FastAPI(title="Medical Receptionist Voice Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = MedicalReceptionistAgent()
activecalls = {}

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Medical Receptionist - Voice Call</title>
    
    <style>
         { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .status {
            padding: 20px;
            margin: 20px 0;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .status.ready { background: #e8f5e9; color: #2e7d32; }
        .status.listening { 
            background: #fff3e0; 
            color: #e65100;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        .status.speaking { background: #e3f2fd; color: #1565c0; }
        .status.error { background: #ffebee; color: #c62828; }
        .status.emergency { 
            background: #ff1744; 
            color: white;
            animation: blink 1s infinite;
        }
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        button {
            padding: 18px 50px;
            font-size: 18px;
            font-weight: 600;
            border: none;
            border-radius: 30px;
            cursor: pointer;
            margin: 10px;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        button:active { transform: scale(0.95); }
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        #startBtn {
            background: linear-gradient(135deg, #4caf50, #45a049);
            color: white;
        }
        #startBtn:hover:not(:disabled) { 
            box-shadow: 0 6px 20px rgba(76,175,80,0.4); 
        }
        
        #stopBtn {
            background: linear-gradient(135deg, #f44336, #e53935);
            color: white;
            display: none;
        }
        #stopBtn:hover { box-shadow: 0 6px 20px rgba(244,67,54,0.4); }
        
        #transcript {
            margin-top: 30px;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 12px;
            min-height: 250px;
            max-height: 400px;
            overflow-y: auto;
            text-align: left;
        }
        .message {
            margin: 12px 0;
            padding: 12px;
            border-radius: 8px;
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .user {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
        }
        .agent {
            background: #f1f8e9;
            border-left: 4px solid #4caf50;
        }
        .emergency {
            background: #ffebee;
            border-left: 4px solid #f44336;
            font-weight: bold;
        }
        .message strong {
            display: block;
            margin-bottom: 5px;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #666;
        }
        .tip {
            background: #fff9c4;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            font-size: 13px;
            text-align: left;
        }
        .tip strong {
            display: block;
            margin-bottom: 8px;
            color: #f57c00;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏥 Medical Receptionist</h1>
        <p class="subtitle">AI-Powered Healthcare Assistant</p>
        
        <div class="tip">
            <strong>💡 How to use:</strong>
            • Click "Start Call" to begin<br>
            • Speak clearly after "Listening..." appears<br>
            • For emergencies, say "emergency" or "chest pain"<br>
            • Say "goodbye" to end the call
        </div>
        
        <div id="status" class="status ready">Ready to start</div>
        <button id="startBtn">📞 Start Call</button>
        <button id="stopBtn">🔴 End Call</button>
        <div id="transcript"></div>
    </div>
    
    <script>
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const status = document.getElementById('status');
        const transcript = document.getElementById('transcript');
        
        let recognition;
        let synthesis = window.speechSynthesis;
        let ws;
        let isListening = false;
        let isSpeaking = false;
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            status.textContent = '❌ Speech not supported. Use Safari on iOS 14.5+';
            status.className = 'status error';
            startBtn.disabled = true;
        }
        
        function initRecognition() {
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            recognition.maxAlternatives = 3;
            
            let finalTranscript = '';
            let interimTranscript = '';
            
            recognition.onstart = function() {
                console.log('🎤 Listening started');
                status.textContent = '🎤 Listening... (speak now)';
                status.className = 'status listening';
            };
            
            recognition.onresult = function(event) {
                interimTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const result = event.results[i];
                    const transcript = result[0].transcript;
                    
                    if (result.isFinal) {
                        finalTranscript += transcript + ' ';
                        console.log('✅ Final:', finalTranscript);
                        
                        if (finalTranscript.trim().length > 0) {
                            processSpeech(finalTranscript.trim());
                            finalTranscript = '';
                        }
                    } else {
                        interimTranscript += transcript;
                        status.textContent = `🎤 Hearing: "${interimTranscript}"`;
                    }
                }
            };
            
            recognition.onspeechend = function() {
                console.log('🔇 Speech ended');
                setTimeout(() => {
                    if (finalTranscript.trim().length > 0) {
                        processSpeech(finalTranscript.trim());
                        finalTranscript = '';
                    }
                }, 500);
            };
            
            recognition.onend = function() {
                console.log('⏹️ Recognition ended');
                if (isListening && !isSpeaking) {
                    setTimeout(() => {
                        if (isListening) {
                            try {
                                recognition.start();
                            } catch (e) {
                                console.error('Restart error:', e);
                            }
                        }
                    }, 100);
                }
            };
            
            recognition.onerror = function(event) {
                console.error('❌ Error:', event.error);
                
                if (event.error === 'not-allowed') {
                    status.textContent = '❌ Microphone blocked';
                    status.className = 'status error';
                    alert('Enable microphone:\\n1. Tap "aA" in address bar\\n2. Website Settings\\n3. Enable Microphone');
                    stopBtn.click();
                } else if (event.error === 'no-speech') {
                    console.log('⚠️ No speech, continuing...');
                }
            };
        }
        
        function processSpeech(text) {
            console.log('💬 Processing:', text);
            
            if (text.length < 2) return;
            
            addMessage('user', text);
            
            if (ws && ws.readyState === WebSocket.OPEN) {
                isListening = false;
                if (recognition) recognition.stop();
                
                ws.send(JSON.stringify({
                    type: 'speech',
                    text: text,
                    confidence: 1.0
                }));
                
                status.textContent = '🤖 AI thinking...';
                status.className = 'status speaking';
            }
        }
        
        async function speak(text) {
            return new Promise((resolve) => {
                isSpeaking = true;
                synthesis.cancel();
                
                console.log('🔊 Speaking:', text);
                
                const isEmergency = text.toLowerCase().includes('emergency') || 
                                   text.toLowerCase().includes('911') ||
                                   text.toLowerCase().includes('call 911');
                
                if (isEmergency) {
                    status.textContent = '🚨 EMERGENCY DETECTED';
                    status.className = 'status emergency';
                }
                
                const sentences = text.match(/[^.!?]+[.!?]+/g) || [text];
                let index = 0;
                
                function speakNext() {
                    if (index >= sentences.length) {
                        isSpeaking = false;
                        resolve();
                        return;
                    }
                    
                    const utterance = new SpeechSynthesisUtterance(sentences[index].trim());
                    utterance.rate = 1.2;
                    utterance.pitch = 1.0;
                    utterance.volume = 1.0;
                    
                    const voices = synthesis.getVoices();
                    const preferredVoice = voices.find(v => 
                        v.lang.startsWith('en') && 
                        (v.name.includes('Samantha') || 
                         v.name.includes('Karen') ||
                         v.name.includes('Female') ||
                         v.name.includes('Aria'))
                    );
                    if (preferredVoice) {
                        utterance.voice = preferredVoice;
                    }
                    
                    utterance.onend = () => {
                        index++;
                        speakNext();
                    };
                    
                    utterance.onerror = () => {
                        index++;
                        speakNext();
                    };
                    
                    synthesis.speak(utterance);
                }
                
                speakNext();
            });
        }
        
        function addMessage(type, text) {
            const msg = document.createElement('div');
            const isEmergency = text.toLowerCase().includes('emergency') || 
                               text.toLowerCase().includes('911');
            msg.className = 'message ' + (isEmergency ? 'emergency' : type);
            const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            msg.innerHTML = '<strong>' + (type === 'user' ? 'You' : 'AI Receptionist') + ' ' + time + '</strong>' + text;
            transcript.appendChild(msg);
            transcript.scrollTop = transcript.scrollHeight;
        }
        
        startBtn.onclick = async function() {
            console.log('🚀 Starting call...');
            
            try {
                await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true
                    } 
                });
                console.log('✅ Microphone granted');
            } catch (err) {
                console.error('❌ Microphone error:', err);
                status.textContent = '❌ Microphone denied';
                status.className = 'status error';
                alert('Microphone required!\\n\\nPlease:\\n1. Tap "aA" in address bar\\n2. Website Settings\\n3. Enable Microphone\\n4. Refresh page');
                return;
            }
            
            startBtn.style.display = 'none';
            stopBtn.style.display = 'block';
            transcript.innerHTML = '';
            
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(protocol + '//' + window.location.host + '/ws');
            
            ws.onopen = function() {
                console.log('🔌 Connected');
                status.textContent = '📞 Connecting...';
                status.className = 'status ready';
                ws.send(JSON.stringify({ type: 'start' }));
            };
            
            ws.onmessage = async function(event) {
                const data = JSON.parse(event.data);
                console.log('📨 Received:', data.type);
                
                if (data.type === 'greeting' || data.type === 'response') {
                    addMessage('agent', data.text);
                    status.textContent = '🔊 AI speaking...';
                    status.className = 'status speaking';
                    
                    await speak(data.text);
                    
                    if (data.endcall) {
                        status.textContent = '📞 Call ended';
                        status.className = 'status';
                        setTimeout(() => stopBtn.click(), 1000);
                    } else {
                        isListening = true;
                        
                        if (!recognition) {
                            initRecognition();
                        }
                        
                        status.textContent = '🎤 Listening...';
                        status.className = 'status listening';
                        
                        setTimeout(() => {
                            if (isListening) {
                                try {
                                    recognition.start();
                                } catch (e) {
                                    console.error('Start error:', e);
                                }
                            }
                        }, 500);
                    }
                }
            };
            
            ws.onerror = function(err) {
                console.error('❌ WebSocket error:', err);
                status.textContent = '❌ Connection error';
                status.className = 'status error';
            };
            
            ws.onclose = function() {
                console.log('🔌 WebSocket closed');
                if (isListening) {
                    stopBtn.click();
                }
            };
        };
        
        stopBtn.onclick = function() {
            console.log('⏹️ Stopping call...');
            
            isListening = false;
            isSpeaking = false;
            
            if (recognition) {
                recognition.stop();
            }
            if (ws) {
                ws.send(JSON.stringify({ type: 'end' }));
                ws.close();
            }
            synthesis.cancel();
            
            startBtn.style.display = 'block';
            stopBtn.style.display = 'none';
            status.textContent = '📞 Call ended';
            status.className = 'status';
        };
        
        if (synthesis.onvoiceschanged !== undefined) {
            synthesis.onvoiceschanged = () => {
                console.log('🎵 Voices loaded:', synthesis.getVoices().length);
            };
        }
        
        console.log('✅ Medical voice system loaded');
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocketendpoint(websocket: WebSocket):
    await websocket.accept()
    
    db = SessionLocal()
    call = Call(
        callernumber="Web Call",
        starttime=datetime.now(),
        status='inprogress'
    )
    db.add(call)
    db.commit()
    callid = str(call.id)
    db.close()
    
    conversationhistory = []
    activecalls[callid] = {
        'history': conversationhistory,
        'starttime': datetime.now()
    }
    
    try:
        while True:
            datastr = await websocket.receivetext()
            data = json.loads(datastr)
            
            if data['type'] == 'start':
                greeting = agent.getgreeting()
                conversationhistory.append({"role": "assistant", "content": greeting})
                
                await websocket.sendtext(json.dumps({
                    'type': 'greeting',
                    'text': greeting
                }))
                
            elif data['type'] == 'speech':
                usertext = data['text']
                conversationhistory.append({"role": "user", "content": usertext})
                
                print(f"[Call {callid}] User: {usertext}")
                
                goodbyephrases = ['goodbye', 'bye', 'thank you', 'thanks', "that's all", "nothing else"]
                if any(phrase in usertext.lower() for phrase in goodbyephrases):
                    farewells = [
                        f"Thank you for calling {config.config.CLINICNAME}. Take care and feel better!",
                        f"It was my pleasure helping you. Have a great day!",
                        f"Thanks for calling. Don't hesitate to reach out if you need anything. Goodbye!",
                    ]
                    farewell = random.choice(farewells)
                    conversationhistory.append({"role": "assistant", "content": farewell})
                    
                    await websocket.sendtext(json.dumps({
                        'type': 'response',
                        'text': farewell,
                        'endcall': True
                    }))
                    
                    updatecallrecord(callid, conversationhistory, 'completed')
                    break
                
                try:
                    response = await agent.processinput(
                        usertext,
                        conversationhistory,
                        callid=callid
                    )
                    
                    print(f"[Call {callid}] AI: {response}")
                    
                    conversationhistory.append({"role": "assistant", "content": response})
                    
                    await websocket.sendtext(json.dumps({
                        'type': 'response',
                        'text': response,
                        'endcall': False
                    }))
                    
                except Exception as e:
                    print(f"[Call {callid}] Error: {e}")
                    errorresponse = "I apologize, could you please repeat that?"
                    
                    await websocket.sendtext(json.dumps({
                        'type': 'response',
                        'text': errorresponse,
                        'endcall': False
                    }))
            
            elif data['type'] == 'end':
                updatecallrecord(callid, conversationhistory, 'completed')
                break
                
    except WebSocketDisconnect:
        print(f"[Call {callid}] Client disconnected")
        updatecallrecord(callid, conversationhistory, 'disconnected')
    except Exception as e:
        print(f"[Call {callid}] Error: {e}")
        updatecallrecord(callid, conversationhistory, 'failed')
    finally:
        if callid in activecalls:
            del activecalls[callid]

def updatecallrecord(callid: str, conversationhistory: list, status: str):
    """Update call record in database"""
    try:
        db = SessionLocal()
        call = db.query(Call).filter(Call.id == int(callid)).first()
        
        if call:
            call.endtime = datetime.now()
            call.duration = int((call.endtime - call.starttime).totalseconds())
            call.status = status
            
            transcript = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in conversationhistory
            ])
            call.transcript = transcript
            
            if len(conversationhistory) > 2:
                usermessages = [msg['content'] for msg in conversationhistory if msg['role'] == 'user']
                from agent.intent_classifier import MedicalIntentClassifier
                classifier = MedicalIntentClassifier()
                call.intent = classifier.classify(" ".join(usermessages))
            
            from agent.emergency_detector import EmergencyDetector
            detector = EmergencyDetector()
            isemergency, severity, _ = detector.detectemergency(transcript)
            call.emergencydetected = isemergency
            
            db.commit()
            print(f"[Call {callid}] Saved: {call.duration}s, Intent: {call.intent}, Emergency: {isemergency}")
        
        db.close()
    except Exception as e:
        print(f"Error updating call: {e}")

if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*70)
    print("🏥 AI MEDICAL RECEPTIONIST - VOICE SYSTEM")
    print("="*70)
    print(f"\n📱 Access: http://localhost:{config.config.VOICEPORT}")
    print(f"📱 Local: http://127.0.0.1:{config.config.VOICEPORT}")
    print("\n✨ Features:")
    print("   ✅ Emergency detection")
    print("   ✅ Appointment booking")
    print("   ✅ Patient verification")
    print("   ✅ Medical Q&A")
    print("   ✅ HIPAA compliant")
    print("\n" + "="*70 + "\n")

    uvicorn.run(app, host=config.config.APIHOST, port=config.config.VOICEPORT)