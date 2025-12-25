import React, { useState, useEffect, useRef } from 'react';
import './ChatInterface.css';

function ChatInterface() {
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState('');
    const [isConnected, setIsConnected] = useState(false);
    const [isWaitingResponse, setIsWaitingResponse] = useState(false);
    const wsRef = useRef(null);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const connectWebSocket = () => {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const ws = new WebSocket(`${protocol}//localhost:8003/ws`);

        ws.onopen = () => {
            console.log('WebSocket connected');
            setIsConnected(true);
            ws.send(JSON.stringify({ type: 'start' }));
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'greeting' || data.type === 'response') {
                setMessages(prev => [...prev, {
                    role: 'agent',
                    content: data.text,
                    timestamp: new Date().toLocaleTimeString()
                }]);
                setIsWaitingResponse(false);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            setIsConnected(false);
        };

        ws.onclose = () => {
            console.log('WebSocket closed');
            setIsConnected(false);
        };

        wsRef.current = ws;
    };

    const disconnectWebSocket = () => {
        if (wsRef.current) {
            wsRef.current.send(JSON.stringify({ type: 'end' }));
            wsRef.current.close();
            wsRef.current = null;
        }
        setIsConnected(false);
        setMessages([]);
    };

    const sendMessage = (e) => {
        e.preventDefault();

        if (!inputText.trim() || !isConnected || isWaitingResponse) return;

        const userMessage = {
            role: 'user',
            content: inputText,
            timestamp: new Date().toLocaleTimeString()
        };

        setMessages(prev => [...prev, userMessage]);

        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'speech',
                text: inputText,
                confidence: 1.0
            }));
        }

        setInputText('');
        setIsWaitingResponse(true);
    };

    const quickMessages = [
        "I need to schedule an appointment",
        "I'm having severe chest pain",
        "I burned my hand and there are blisters",
        "I have a small cut on my finger",
        "What are the symptoms of high blood pressure?",
        "When is my next appointment?",
        "Thank you, goodbye"
    ];

    return (
        <div className="chat-interface">
            <div className="chat-container">
                <div className="chat-header">
                    <h2>💬 Text Chat Interface</h2>
                    <p>Test the AI Medical Receptionist via text</p>
                    <div className="connection-controls">
                        {!isConnected ? (
                            <button className="connect-btn" onClick={connectWebSocket}>
                                🔌 Connect to AI
                            </button>
                        ) : (
                            <button className="disconnect-btn" onClick={disconnectWebSocket}>
                                🔴 Disconnect
                            </button>
                        )}
                        <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
                            {isConnected ? '🟢 Connected' : '⚫ Disconnected'}
                        </span>
                    </div>
                </div>

                <div className="chat-messages">
                    {messages.length === 0 && (
                        <div className="welcome-message">
                            <h3>👋 Welcome to the AI Medical Receptionist</h3>
                            <p>Click "Connect to AI" to start a conversation, or use the quick test buttons below.</p>
                        </div>
                    )}

                    {messages.map((msg, index) => (
                        <div key={index} className={`message ${msg.role}`}>
                            <div className="message-header">
                                <strong>{msg.role === 'user' ? '👤 You' : '🤖 AI Receptionist'}</strong>
                                <span className="timestamp">{msg.timestamp}</span>
                            </div>
                            <div className="message-content">{msg.content}</div>
                        </div>
                    ))}

                    {isWaitingResponse && (
                        <div className="message agent typing">
                            <div className="message-header">
                                <strong>🤖 AI Receptionist</strong>
                            </div>
                            <div className="message-content">
                                <span className="typing-indicator">
                                    <span>.</span><span>.</span><span>.</span>
                                </span>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                <div className="quick-messages">
                    <p><strong>Quick Test Messages:</strong></p>
                    <div className="quick-buttons">
                        {quickMessages.map((msg, index) => (
                            <button
                                key={index}
                                className="quick-btn"
                                onClick={() => {
                                    if (isConnected && !isWaitingResponse) {
                                        setInputText(msg);
                                    }
                                }}
                                disabled={!isConnected || isWaitingResponse}
                            >
                                {msg}
                            </button>
                        ))}
                    </div>
                </div>

                <form className="chat-input-form" onSubmit={sendMessage}>
                    <input
                        type="text"
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        placeholder={isConnected ? "Type your message..." : "Connect first to chat"}
                        disabled={!isConnected || isWaitingResponse}
                        className="chat-input"
                    />
                    <button
                        type="submit"
                        className="send-btn"
                        disabled={!isConnected || !inputText.trim() || isWaitingResponse}
                    >
                        📤 Send
                    </button>
                </form>

                <div className="chat-info">
                    <p><strong>💡 Features:</strong></p>
                    <ul>
                        <li>✅ TTS (Text-to-Speech): Implemented in voice interface</li>
                        <li>✅ STT (Speech-to-Text): Implemented in voice interface</li>
                        <li>💬 This chat: Text-only for easy testing</li>
                        <li>🚨 Emergency detection active</li>
                        <li>🩺 8-step medical triage process</li>
                    </ul>
                </div>
            </div>
        </div>
    );
}

export default ChatInterface;
