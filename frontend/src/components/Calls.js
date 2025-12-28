import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Calls.css';

function Calls() {
    const [calls, setCalls] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedCall, setSelectedCall] = useState(null);

    useEffect(() => {
        fetchCalls();
        const interval = setInterval(fetchCalls, 5000); // Polling for updates
        return () => clearInterval(interval);
    }, []);

    const fetchCalls = async () => {
        try {
            const response = await axios.get('/api/calls');
            // Sort by starttime descending
            const sortedCalls = response.data.sort((a, b) => new Date(b.starttime) - new Date(a.starttime));
            setCalls(sortedCalls);
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
        if (!seconds) return '—';
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}m ${secs}s`;
    };

    const emergenciesCount = calls.filter(c => c.emergencydetected).length;

    if (loading) return (
        <div className="loading-container">
            <div className="spinner"></div>
            <p>Loading call history...</p>
        </div>
    );

    return (
        <div className="calls-page">
            <div className="page-header">
                <div className="header-content">
                    <div>
                        <h2>📞 Call History</h2>
                        <p style={{ color: '#64748b', marginTop: '5px' }}>Voice interactions with the reception agent.</p>
                    </div>
                    <div className="stats-summary">
                        <span className="stat-badge">
                            <strong>{calls.length}</strong> Total Calls
                        </span>
                        {emergenciesCount > 0 && (
                            <span className="stat-badge emergency-stat">
                                <strong>{emergenciesCount}</strong> Emergencies Detected
                            </span>
                        )}
                    </div>
                </div>
            </div>

            <div className="table-container">
                {calls.length === 0 ? (
                    <div className="no-results">
                        <div className="no-results-icon">📞</div>
                        <h3>No calls recorded yet</h3>
                        <p>Incoming calls will appear here in real-time.</p>
                    </div>
                ) : (
                    <table className="calls-table">
                        <thead>
                            <tr>
                                <th>Status</th>
                                <th>Caller</th>
                                <th>Date & Time</th>
                                <th>Duration</th>
                                <th>Intent</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {calls.map(call => (
                                <tr key={call.id} onClick={() => viewCallDetails(call.id)} style={{ cursor: 'pointer' }}>
                                    <td>
                                        <span className={`status-badge ${call.status && call.status.toLowerCase()}`}>
                                            {call.status || 'Unknown'}
                                        </span>
                                    </td>
                                    <td>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            <span style={{ fontSize: '18px' }}>{call.emergencydetected ? '🚨' : '👤'}</span>
                                            <strong>{call.callername || 'Unknown Caller'}</strong>
                                        </div>
                                    </td>
                                    <td>
                                        {new Date(call.starttime).toLocaleString()}
                                    </td>
                                    <td>{formatDuration(call.duration)}</td>
                                    <td>
                                        <span className={`intent-badge ${call.intent || 'info'}`}>
                                            {call.intent || 'Unclassified'}
                                        </span>
                                    </td>
                                    <td>
                                        <button className="action-btn view-btn" onClick={(e) => { e.stopPropagation(); viewCallDetails(call.id); }}>
                                            📜 Transcript
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {selectedCall && (
                <div className="call-modal" onClick={() => setSelectedCall(null)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <h3>📜 Call Transcript</h3>
                            <button className="close-btn" onClick={() => setSelectedCall(null)}>Close</button>
                        </div>

                        <div style={{ margin: '10px 0', padding: '10px', background: '#f1f5f9', borderRadius: '4px' }}>
                            <p><strong>Caller:</strong> {selectedCall.callername || 'Unknown'}</p>
                            <p><strong>Date:</strong> {new Date(selectedCall.starttime).toLocaleString()}</p>
                            <p><strong>Intent:</strong> {selectedCall.intent}</p>
                        </div>

                        <div className="transcript">
                            {selectedCall.transcript && selectedCall.transcript.length > 0 ? (
                                selectedCall.transcript.map((msg, idx) => (
                                    <div key={idx} className={`message ${msg.role}`}>
                                        <strong>{msg.role === 'assistant' ? '🤖 Agent' : '👤 Caller'}</strong>
                                        {msg.content}
                                    </div>
                                ))
                            ) : (
                                <p style={{ color: '#94a3b8', textAlign: 'center' }}>No transcript available for this call.</p>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Calls;
