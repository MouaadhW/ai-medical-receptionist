import React, { useState, useEffect } from 'react';
import GlassCard from '../shared/GlassCard';
import AITooltip from '../shared/AITooltip';
import { AnatomyPicker, AdultMaleFront, AdultMaleBack, AdultFemaleFront, AdultFemaleBack } from "react-anatomy-picker";
import './history.css';

const NeuralHistory = () => {
    const [events, setEvents] = useState([]);
    const [viewMode, setViewMode] = useState('timeline');  // timeline, anatomical, list
    const [loading, setLoading] = useState(true);
    const [selectedParts, setSelectedParts] = useState([]);
    const [gender, setGender] = useState('male');
    const [bodyView, setBodyView] = useState('front');
    const [anatomicalData, setAnatomicalData] = useState({});
    const [showAddModal, setShowAddModal] = useState(false);
    const [formData, setFormData] = useState({
        event_type: 'visit',
        title: '',
        description: '',
        event_date: new Date().toISOString().split('T')[0],
        severity: 'low',
        status: 'active',
        provider_name: '',
        facility_name: '',
        anatomical_locations: []
    });

    useEffect(() => {
        fetchMedicalHistory();
    }, []);

    const fetchMedicalHistory = async () => {
        try {
            const patientId = 1; // TODO: Get from auth context

            // Fetch Filterable Timeline
            const responseV1 = await fetch(`http://localhost:8000/api/history/patient/${patientId}`);
            const dataV1 = await responseV1.json();
            setEvents(dataV1.events || []);

            // Fetch Anatomical Map
            const responseV2 = await fetch(`http://localhost:8000/api/history/anatomical/${patientId}`);
            const dataV2 = await responseV2.json();
            setAnatomicalData(dataV2.anatomical_map || {});

        } catch (error) {
            console.error('Error fetching medical history:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmitEvent = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch('http://localhost:8000/api/history/events/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    patient_id: 1,
                    ...formData
                })
            });

            if (response.ok) {
                await fetchMedicalHistory();
                setShowAddModal(false);
                setFormData({
                    event_type: 'visit',
                    title: '',
                    description: '',
                    event_date: new Date().toISOString().split('T')[0],
                    severity: 'low',
                    status: 'active',
                    provider_name: '',
                    facility_name: '',
                    anatomical_locations: []
                });
            }
        } catch (error) {
            console.error('Error creating event:', error);
        }
    };

    const getSeverityColor = (severity) => {
        const colors = {
            critical: '#ef4444',
            high: '#f59e0b',
            medium: '#f59e0b',
            low: '#10b981'
        };
        return colors[severity] || colors.low;
    };

    const getSeverityIcon = (severity) => {
        const icons = {
            critical: '🔴',
            high: '🟠',
            medium: '🟡',
            low: '🟢'
        };
        return icons[severity] || icons.low;
    };

    const getEventTypeIcon = (type) => {
        const icons = {
            diagnosis: '🩺',
            procedure: '⚕️',
            visit: '🏥',
            test: '🔬',
            medication: '💊',
            vaccination: '💉'
        };
        return icons[type] || '📋';
    };

    if (loading) {
        return <div className="skeleton" style={{ height: '600px' }}></div>;
    }

    return (
        <div className="neural-history animate-fadeInUp">
            <div className="history-header">
                <h1 className="gradient-text-timeline">🧠 Neural History</h1>
                <p className="subtitle">Your complete medical journey visualized</p>
            </div>

            {/* View Mode Toggle */}
            <div className="view-toggle glass">
                <button
                    className={`toggle-btn ${viewMode === 'timeline' ? 'active' : ''}`}
                    onClick={() => setViewMode('timeline')}
                >
                    📅 Timeline
                </button>
                <button
                    className={`toggle-btn ${viewMode === 'anatomical' ? 'active' : ''}`}
                    onClick={() => setViewMode('anatomical')}
                >
                    🫀 Anatomical
                </button>
                <button
                    className={`toggle-btn ${viewMode === 'list' ? 'active' : ''}`}
                    onClick={() => setViewMode('list')}
                >
                    📋 List
                </button>
            </div>

            {/* Stats Overview */}
            <div className="stats-grid">
                <GlassCard variant="light" className="stat-card">
                    <div className="stat-value">{events.length}</div>
                    <div className="stat-label">Total Events</div>
                </GlassCard>
                <GlassCard variant="light" className="stat-card">
                    <div className="stat-value">
                        {events.filter(e => e.status === 'follow_up_needed').length}
                    </div>
                    <div className="stat-label">Follow-ups Needed</div>
                </GlassCard>
                <GlassCard variant="light" className="stat-card">
                    <div className="stat-value">
                        {events.length ? new Date(Math.max(...events.map(e => new Date(e.event_date)))).getFullYear() - new Date(Math.min(...events.map(e => new Date(e.event_date)))).getFullYear() : 0} years
                    </div>
                    <div className="stat-label">History Span</div>
                </GlassCard>
            </div>

            {/* Timeline View */}
            {viewMode === 'timeline' && (
                <div className="timeline-view">
                    <div className="timeline-line"></div>
                    {[...events].sort((a, b) => new Date(b.event_date) - new Date(a.event_date)).map((event, index) => (
                        <div
                            key={event.id}
                            className="timeline-event animate-fadeInScale"
                            style={{ animationDelay: `${index * 0.1}s` }}
                        >
                            <div className="timeline-marker" style={{ background: getSeverityColor(event.severity) }}>
                                {getSeverityIcon(event.severity)}
                            </div>
                            <GlassCard variant="medium" animated className="event-card hover-lift">
                                <div className="event-header">
                                    <div className="event-type-badge">
                                        {getEventTypeIcon(event.event_type)} {event.event_type}
                                    </div>
                                    <div className="event-date">
                                        {new Date(event.event_date).toLocaleDateString()}
                                    </div>
                                </div>
                                <h3 className="event-title">{event.title}</h3>
                                <p className="event-description">{event.description}</p>
                                {event.provider_name && (
                                    <div className="event-meta">
                                        <span>👨‍⚕️ {event.provider_name}</span>
                                        {event.facility_name && <span>🏥 {event.facility_name}</span>}
                                    </div>
                                )}
                                <div className="event-footer">
                                    <span className={`status-badge status-${event.status}`}>
                                        {event.status.replace('_', ' ').toUpperCase()}
                                    </span>
                                    <AITooltip content="Click for AI insights about this event">
                                        <button className="btn-insights">🤖 View Insights</button>
                                    </AITooltip>
                                </div>
                            </GlassCard>
                        </div>
                    ))}
                </div>
            )}

            {/* Anatomical View */}
            {viewMode === 'anatomical' && (
                <div className="anatomical-view">
                    <div className="anatomical-split-view">
                        <GlassCard variant="heavy" className="body-map-container">
                            <div className="anatomy-controls">
                                <div className="gender-selector">
                                    <button
                                        className={`gender-btn ${gender === 'male' ? 'active' : ''}`}
                                        onClick={() => setGender('male')}
                                    >
                                        👨 Male
                                    </button>
                                    <button
                                        className={`gender-btn ${gender === 'female' ? 'active' : ''}`}
                                        onClick={() => setGender('female')}
                                    >
                                        👩 Female
                                    </button>
                                </div>
                                <div className="view-selector">
                                    <button
                                        className={`view-btn ${bodyView === 'front' ? 'active' : ''}`}
                                        onClick={() => setBodyView('front')}
                                    >
                                        Front
                                    </button>
                                    <button
                                        className={`view-btn ${bodyView === 'back' ? 'active' : ''}`}
                                        onClick={() => setBodyView('back')}
                                    >
                                        Back
                                    </button>
                                </div>
                            </div>

                            <div className="anatomy-picker-wrapper">
                                <AnatomyPicker
                                    SvgComponent={
                                        gender === 'male'
                                            ? (bodyView === 'front' ? AdultMaleFront : AdultMaleBack)
                                            : (bodyView === 'front' ? AdultFemaleFront : AdultFemaleBack)
                                    }
                                    selected={selectedParts}
                                    highlightColor="#2DD4BF"
                                    onPartSelect={(part) => {
                                        setSelectedParts(prev =>
                                            prev.includes(part) ? prev.filter(p => p !== part) : [...prev, part]
                                        );
                                    }}
                                    style={{ width: '100%', maxWidth: '300px', margin: '0 auto' }}
                                />
                            </div>

                            <div className="manual-select-container">
                                <p className="manual-select-label">Quick Select:</p>
                                <div className="quick-select-grid">
                                    {['head', 'chest', 'stomach', 'left_shoulder', 'right_shoulder', 'left_arm', 'right_arm', 'left_leg', 'right_leg'].map(part => (
                                        <button
                                            key={part}
                                            className={`quick-select-btn ${selectedParts.includes(part) ? 'active' : ''}`}
                                            onClick={() => {
                                                setSelectedParts(prev =>
                                                    prev.includes(part) ? prev.filter(p => p !== part) : [...prev, part]
                                                );
                                            }}
                                        >
                                            {part.replace(/_/g, ' ')}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </GlassCard>

                        <div className="anatomical-details-panel">
                            <GlassCard variant="light" className="details-card">
                                <div className="details-header">
                                    <h3>🧬 Medical Records for Selection</h3>
                                    <span className="selection-count">{selectedParts.length} regions selected</span>
                                </div>

                                {selectedParts.length === 0 ? (
                                    <div className="empty-state-anatomy">
                                        <div className="empty-icon">👆</div>
                                        <p>Select a body part to view related history</p>
                                    </div>
                                ) : (
                                    <div className="filtered-events-list">
                                        {selectedParts.map(part => {
                                            const dbKey = part.replace(/-/g, '_').toLowerCase();
                                            const partEvents = anatomicalData[dbKey] || [];

                                            return (
                                                <div key={part} className="anatomy-section-group">
                                                    <h4 className="anatomy-section-title">{part.replace(/_/g, ' ')} ({partEvents.length})</h4>
                                                    {partEvents.length > 0 ? (
                                                        partEvents.map(({ event, location_details }) => (
                                                            <div key={event.id} className="mini-event-card">
                                                                <div className="mini-event-header">
                                                                    <span className={`status-dot status-${event.status}`}></span>
                                                                    <span className="mini-event-date">{new Date(event.event_date).toLocaleDateString()}</span>
                                                                </div>
                                                                <h5>{event.title}</h5>
                                                                <p>{event.description}</p>
                                                                {location_details.specific_location && (
                                                                    <div className="location-tag">📍 {location_details.specific_location}</div>
                                                                )}
                                                            </div>
                                                        ))
                                                    ) : (
                                                        <p className="no-events-text">No records found for this region.</p>
                                                    )}
                                                </div>
                                            );
                                        })}
                                    </div>
                                )}
                            </GlassCard>
                        </div>
                    </div>
                </div>
            )}

            {/* List View */}
            {viewMode === 'list' && (
                <div className="list-view">
                    <table className="events-table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Type</th>
                                <th>Title</th>
                                <th>Provider</th>
                                <th>Severity</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {events.map(event => (
                                <tr key={event.id} className="table-row">
                                    <td>{new Date(event.event_date).toLocaleDateString()}</td>
                                    <td>
                                        <span className="type-badge">
                                            {getEventTypeIcon(event.event_type)} {event.event_type}
                                        </span>
                                    </td>
                                    <td className="title-cell">{event.title}</td>
                                    <td>{event.provider_name || '—'}</td>
                                    <td>
                                        <span className="severity-indicator" style={{ background: getSeverityColor(event.severity) }}>
                                            {event.severity}
                                        </span>
                                    </td>
                                    <td>
                                        <span className={`status-badge status-${event.status}`}>
                                            {event.status.replace('_', ' ')}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* FAB - Add Event Button */}
            <button className="fab" onClick={() => setShowAddModal(true)}>
                <span className="fab-icon">+</span>
            </button>

            {/* Add Event Modal */}
            {showAddModal && (
                <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
                    <GlassCard variant="heavy" className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>➕ Add Medical Event</h2>
                            <button className="close-btn" onClick={() => setShowAddModal(false)}>×</button>
                        </div>
                        <form onSubmit={handleSubmitEvent} className="event-form">
                            <div className="form-row">
                                <div className="form-group">
                                    <label>Event Type</label>
                                    <select
                                        value={formData.event_type}
                                        onChange={(e) => setFormData({ ...formData, event_type: e.target.value })}
                                        required
                                    >
                                        <option value="visit">Visit</option>
                                        <option value="diagnosis">Diagnosis</option>
                                        <option value="procedure">Procedure</option>
                                        <option value="test">Test</option>
                                        <option value="medication">Medication</option>
                                        <option value="vaccination">Vaccination</option>
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label>Event Date</label>
                                    <input
                                        type="date"
                                        value={formData.event_date}
                                        onChange={(e) => setFormData({ ...formData, event_date: e.target.value })}
                                        required
                                    />
                                </div>
                            </div>

                            <div className="form-group">
                                <label>Title</label>
                                <input
                                    type="text"
                                    value={formData.title}
                                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                    placeholder="e.g., Annual Checkup, Flu Vaccination"
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label>Description</label>
                                <textarea
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    placeholder="Describe the medical event..."
                                    rows="3"
                                    required
                                />
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label>Severity</label>
                                    <select
                                        value={formData.severity}
                                        onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                                    >
                                        <option value="low">Low</option>
                                        <option value="medium">Medium</option>
                                        <option value="high">High</option>
                                        <option value="critical">Critical</option>
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label>Status</label>
                                    <select
                                        value={formData.status}
                                        onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                                    >
                                        <option value="active">Active</option>
                                        <option value="resolved">Resolved</option>
                                        <option value="ongoing">Ongoing</option>
                                        <option value="follow_up_needed">Follow-up Needed</option>
                                    </select>
                                </div>
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label>Provider Name</label>
                                    <input
                                        type="text"
                                        value={formData.provider_name}
                                        onChange={(e) => setFormData({ ...formData, provider_name: e.target.value })}
                                        placeholder="Dr. Smith"
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Facility Name</label>
                                    <input
                                        type="text"
                                        value={formData.facility_name}
                                        onChange={(e) => setFormData({ ...formData, facility_name: e.target.value })}
                                        placeholder="City Hospital"
                                    />
                                </div>
                            </div>

                            <div className="form-actions">
                                <button type="button" className="btn-cancel" onClick={() => setShowAddModal(false)}>
                                    Cancel
                                </button>
                                <button type="submit" className="btn-submit">
                                    ✓ Add Event
                                </button>
                            </div>
                        </form>
                    </GlassCard>
                </div>
            )}
        </div>
    );
};

export default NeuralHistory;
