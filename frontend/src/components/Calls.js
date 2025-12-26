import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Calls() {
    const [calls, setCalls] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedCall, setSelectedCall] = useState(null);

    useEffect(() => {
        fetchCalls();
    }, []);

    const fetchCalls = async () => {
        try {
            const response = await axios.get('/api/calls');
            setCalls(response.data);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching calls:', error);
            setLoading(false);
        }
    };

    const viewCallDetails = async (callId) => {
        try {
            const response = await axios.get(`/api/calls/${callId}`);
            setSelectedCall(response.data);
        } catch (error) {
            console.error('Error fetching call details:', error);
        }
    };

    const formatDuration = (seconds) => {
        if (!seconds) return 'N/A';
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}m ${secs}s`;
    };

    if (loading) return <div className="loading">Loading calls...</div>;

    return (
        <div className="calls-container">
            <h2>📞 Call History</h2>

            <div className="calls-list">
                {calls.length === 0 ? (
                    <div className="no-calls">No calls recorded</div>
                ) : (
                    calls.map(call => (
                        <div
                            key={call.id}
                            className={`call-card ${call.emergencydetected ? 'emergency' : ''}`}
                            onClick={() => viewCallDetails(call.id)}
                        >
                            <div className="call-header">
                                <span className="call-icon">
                                    {call.emergencydetected ? '🚨' : '📞'}
                                </span>
                                <div className="call-info">
                                    <h3>{call.callername || 'Unknown Caller'}</h3>
                                    <p className="call-time">
                                        {new Date(call.starttime).toLocaleString()}
                                    </p>
                                </div>
                            </div>
                            <div className="call-details">
                                <p><strong>Duration:</strong> {formatDuration(call.duration)}</p>
                                <p><strong>Intent:</strong> {call.intent || 'Not classified'}</p>
                                <span className={`status-badge ${call.status}`}>
                                    {call.status}
                                </span>
                                {call.emergencydetected && (
                                    <span className="emergency-badge">EMERGENCY</span>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>

            {selectedCall && (
                <div className="call-modal" onClick={() => setSelectedCall(null)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h3>Call Transcript</h3>
                        <div className="transcript">
                            {selectedCall.transcript && selectedCall.transcript.length > 0 ? (
                                selectedCall.transcript.map((msg, idx) => (
                                    <div key={idx} className={`message ${msg.role}`}>
                                        <strong>{msg.role}:</strong> {msg.content}
                                    </div>
                                ))
                            ) : (
                                <p>No transcript available</p>
                            )}
                        </div>
                        <button onClick={() => setSelectedCall(null)}>Close</button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Calls;
