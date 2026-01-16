import React, { useEffect, useState, useRef, useCallback } from 'react';
import './PhoneInterface.css';

const PhoneInterface = () => {
  const [status, setStatus] = useState('idle'); // idle, connecting, listening, speaking, emergency
  const [transcript, setTranscript] = useState([]);
  const [error, setError] = useState(null);

  // Refs for audio handling to avoid re-renders
  const ws = useRef(null);
  const audioContext = useRef(null);
  const audioQueue = useRef([]);
  const isPlaying = useRef(false);
  const nextStartTime = useRef(0);
  const streamRef = useRef(null);
  const processorRef = useRef(null);
  const statusRef = useRef('idle'); // Track status in ref for callbacks

  // Sync statusRef with status state changes
  useEffect(() => {
    statusRef.current = status;
  }, [status]);

  const appendTranscript = (role, text) => {
    setTranscript(prev => [...prev, { role, text, time: new Date().toLocaleTimeString() }]);
  };

  const playNextAudio = useCallback(() => {
    if (audioQueue.current.length === 0) {
      isPlaying.current = false;
      // Slight delay before switching back to listening to avoid capturing echo
      setTimeout(() => setStatus('listening'), 300);
      return;
    }

    isPlaying.current = true;
    setStatus('speaking');

    const audioData = audioQueue.current.shift();
    const buffer = audioContext.current.createBuffer(1, audioData.length, 16000); // 16kHz server rate
    buffer.getChannelData(0).set(audioData);

    const source = audioContext.current.createBufferSource();
    source.buffer = buffer;
    source.connect(audioContext.current.destination);

    // Ensure seamless playback by scheduling
    const currentTime = audioContext.current.currentTime;
    const start = Math.max(currentTime, nextStartTime.current);

    source.start(start);
    nextStartTime.current = start + buffer.duration;

    source.onended = () => {
      // Check if queue empty inside the callback to chain correctly
      if (audioQueue.current.length === 0) {
        playNextAudio();
      }
    };

    // If we have more in queue, try to schedule logically (simplified here to sequential)
    if (audioQueue.current.length > 0) {
      // The onended handles the loop, but for very fast chunks we might want to schedule ahead.
      // For now, simple sequential play is safer to avoid overlap.
    }
  }, [status]); // Dependencies might need tuning

  const handleAudioMessage = useCallback((data) => {
    // Convert Int16 bytes to Float32
    const int16Array = new Int16Array(data);
    const float32Array = new Float32Array(int16Array.length);

    for (let i = 0; i < int16Array.length; i++) {
      float32Array[i] = int16Array[i] / 32768.0;
    }

    audioQueue.current.push(float32Array);

    if (!isPlaying.current) {
      playNextAudio();
    }
  }, [playNextAudio]);

  const connectWebSocket = useCallback(() => {
    setStatus('connecting');
    // Pointing to localhost:8003 where voice_server.py is running
    const socket = new WebSocket('ws://localhost:8003/ws');

    socket.onopen = () => {
      console.log('✅ Connected to Voice Server');
      setStatus('listening');
      // The server sends a greeting immediately, so we just wait
    };

    socket.onmessage = async (event) => {
      if (typeof event.data === 'string') {
        // Control message
        const msg = JSON.parse(event.data);

        if (msg.type === 'response') {
          // Metadata for upcoming audio
          if (msg.text) appendTranscript('agent', msg.text);
        } else if (msg.type === 'transcript') {
          // Add user transcript to the chat window
          appendTranscript('user', msg.text);
          console.log("User transcript:", msg.text);
        }
      } else if (event.data instanceof Blob) {
        // Binary Audio Data
        const arrayBuffer = await event.data.arrayBuffer();
        handleAudioMessage(arrayBuffer);
      }
    };

    socket.onerror = (e) => {
      console.error('WebSocket Error:', e);
      setError('Connection failed. Is the backend running?');
      setStatus('error');
    };

    socket.onclose = () => {
      console.log('WebSocket Closed');
      if (status === 'listening' || status === 'speaking') {
        console.log('Attempting reconnect...');
        setTimeout(connectWebSocket, 1000);
      } else {
        setStatus('idle');
      }
    };

    ws.current = socket;
  }, [handleAudioMessage]);

  const startMicrophone = async () => {
    try {
      audioContext.current = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          channelCount: 1,
          sampleRate: 16000
        }
      });
      streamRef.current = stream;

      const source = audioContext.current.createMediaStreamSource(stream);

      // Use ScriptProcessor for legacy compatibility or AudioWorklet (ScriptProcessor easier to shim quickly)
      // Buffer size 4096 gives ~250ms latency but is stable. 2048 or 1024 for lower latency.
      const processor = audioContext.current.createScriptProcessor(4096, 1, 1);

      let chunkCount = 0; // Debug counter

      processor.onaudioprocess = (e) => {
        // Use statusRef to get current status (avoid closure issues)
        const currentStatus = statusRef.current;

        // Debug logging (throttle)
        chunkCount++;
        if (chunkCount % 50 === 0) {
          console.log(`[AudioProc] Status: ${currentStatus}, isPlaying: ${isPlaying.current}`);
        }

        // Only record when connected (not idle/error/connecting)
        if (currentStatus === 'idle' || currentStatus === 'error' || currentStatus === 'connecting') return;

        // Don't record while agent is actively playing audio (half-duplex - simple echo cancellation)
        if (isPlaying.current) return;

        const inputData = e.inputBuffer.getChannelData(0);

        // Calculate RMS for debug
        let sum = 0;
        for (let i = 0; i < inputData.length; i++) {
          sum += inputData[i] * inputData[i];
        }
        const rms = Math.sqrt(sum / inputData.length);

        if (chunkCount % 50 === 0) {
          console.log(`[AudioProc] Input RMS: ${rms.toFixed(4)}`);
        }
        const inputSampleRate = audioContext.current.sampleRate;
        const targetSampleRate = 16000;

        // Simple Downsampling: Skip samples
        // Note: For high quality, a low-pass filter (decimation) is better, but this suffices for VAD.
        const compression = inputSampleRate / targetSampleRate;
        const resultLength = Math.ceil(inputData.length / compression);
        const pcmData = new Int16Array(resultLength);

        for (let i = 0; i < resultLength; i++) {
          // Nearest neighbor interpolation (fastest)
          const inputIndex = Math.floor(i * compression);
          // Clamp and convert
          let s = Math.max(-1, Math.min(1, inputData[inputIndex]));
          pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }

        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
          ws.current.send(pcmData.buffer);
          if (chunkCount % 50 === 0) console.log("[WS] Sent audio buffer");
        } else {
          if (chunkCount % 50 === 0) console.warn(`[WS] Not open. State: ${ws.current ? ws.current.readyState : 'null'}`);
        }
      };

      source.connect(processor);
      processor.connect(audioContext.current.destination); // Needed for Chrome to activate processor
      processorRef.current = processor;

      connectWebSocket();

    } catch (err) {
      console.error('Microphone Error:', err);
      setError('Microphone access denied');
    }
  };

  const stopCall = () => {
    if (ws.current) ws.current.close();
    if (streamRef.current) streamRef.current.getTracks().forEach(track => track.stop());
    if (audioContext.current) audioContext.current.close();
    setStatus('idle');
  };

  useEffect(() => {
    return () => {
      stopCall();
    };
  }, []);

  return (
    <div className={`phone-interface ${status}`}>
      <div className="phone-container">
        <div className="phone-header">
          <h2>🏥 AI Medical Receptionist</h2>
          <div className={`status-badge ${status}`}>
            {status === 'idle' && 'Ready to Call'}
            {status === 'connecting' && 'Connecting...'}
            {status === 'listening' && '🎤 AI Listening...'}
            {status === 'speaking' && '🔊 AI Speaking'}
            {status === 'error' && '❌ Error'}
          </div>
        </div>

        <div className="transcript-area">
          {transcript.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              <div className="message-bubble">{msg.text}</div>
              <span className="timestamp">{msg.time}</span>
            </div>
          ))}
          {transcript.length === 0 && (
            <div className="placeholder">
              <p>👋 Click "Start Call" to speak with the receptionist.</p>
              <p>Try saying: "I'd like to book an appointment" or "I have a fever"</p>
            </div>
          )}
        </div>

        <div className="controls">
          {status === 'idle' || status === 'error' ? (
            <button className="btn-call start" onClick={startMicrophone}>
              📞 Start Call
            </button>
          ) : (
            <button className="btn-call stop" onClick={stopCall}>
              🔴 End Call
            </button>
          )}
        </div>

        {error && <div className="error-banner">{error}</div>}
      </div>
    </div>
  );
};

export default PhoneInterface;
