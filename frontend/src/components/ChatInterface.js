import React, { useState, useEffect, useRef } from 'react';
import './ChatInterface.css';
import { WS_BASE_URL } from '../config';

function ChatInterface() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isConnected, setIsConnected] = useState(false);
    const [isWaitingResponse, setIsWaitingResponse] = useState(false);
    const ws = useRef(null);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const connectWebSocket = () => {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const token = localStorage.getItem('token');
        console.log('Connecting with token:', token ? token.substring(0, 10) + '...' : 'None');
        const url = token
            ? `${protocol}//localhost:8003/ws?token=${token}`
            : `${protocol}//localhost:8003/ws`;
        const ws = new WebSocket(url);

        ws.onopen = () => {
            console.log('WebSocket connected');
            setIsConnected(true);
            ws.send(JSON.stringify({ type: 'start' }));
        };

        ws.onmessage = (event) => {
            // Check if data is a Blob (binary audio data)
            if (event.data instanceof Blob) {
                // Ignore audio data in text chat interface
                // console.log('Received audio blob, ignoring in text interface');
                return;
            }

            // Ensure we have string data before attempting JSON.parse
            if (typeof event.data !== 'string') {
                console.warn('Received non-string, non-Blob data:', typeof event.data);
                return;
            }

            try {
                const data = JSON.parse(event.data);

                if (data.type === 'greeting' || data.type === 'response') {
                    setMessages(prev => [...prev, {
                        role: 'agent',
                        content: data.text,
                        timestamp: new Date().toLocaleTimeString()
                    }]);
                    setIsWaitingResponse(false);
                }
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
                console.error('Problematic data:', event.data);
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

            </div>
        </div>
    );
}

export default ChatInterface;
