import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import AppointmentHistory from './AppointmentHistory';
import './UserDashboard.css';

const UserDashboard = () => {
    const { user } = useAuth();
    const navigate = useNavigate();

    return (
        <div className="user-dashboard-container">
            <div className="dashboard-logo-section">
                <img src="/assets/medpulse-logo.png" alt="MedPulse" className="dashboard-logo" />
                <h2>Welcome, {user.username}!</h2>
            </div>

            <div className="dashboard-grid">
                <div className="card dashboard-card">
                    <div className="card-header">
                        <span className="card-icon">👤</span>
                        <h3>Your Profile</h3>
                    </div>
                    <div className="card-body">
                        <div className="profile-item">
                            <label>Username</label>
                            <p>{user.username}</p>
                        </div>
                        <div className="profile-item">
                            <label>Email</label>
                            <p>{user.email}</p>
                        </div>
                        <div className="profile-item">
                            <label>Account Type</label>
                            <p className="badge badge-primary">{user.role}</p>
                        </div>
                        <div className="otid-box">
                            <label>Your Security Code (OTID)</label>
                            <div className="otid-display">{user.otid}</div>
                            <small>Provide this code when speaking with the AI Agent to verify your identity.</small>
                        </div>
                    </div>
                </div>

                <div className="card dashboard-card">
                    <div className="card-header">
                        <span className="card-icon">🏥</span>
                        <h3>Quick Actions</h3>
                    </div>
                    <div className="card-body">
                        <p className="text-muted">Connect with our AI Medical Assistant</p>
                        <div className="action-buttons">
                            <button
                                className="btn btn-primary btn-large"
                                onClick={() => navigate('/phone')}
                            >
                                📞 Voice Call
                            </button>
                            <button
                                className="btn btn-secondary btn-large"
                                onClick={() => navigate('/chat')}
                            >
                                💬 Chat
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <AppointmentHistory />
        </div>
    );
};

export default UserDashboard;
