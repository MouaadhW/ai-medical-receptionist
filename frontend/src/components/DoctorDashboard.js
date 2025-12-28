import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import './Dashboard.css';
import './Doctors.css'; // Import the new styles

const DoctorDashboard = () => {
    const { user } = useAuth();
    const [schedule, setSchedule] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchSchedule();
    }, []);

    const fetchSchedule = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('http://localhost:8000/api/doctor/my-schedule', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (response.ok) {
                const data = await response.json();
                setSchedule(data);
            }
        } catch (error) {
            console.error('Error fetching schedule:', error);
        } finally {
            setLoading(false);
        }
    };

    // Filter appointments
    const today = new Date().toISOString().split('T')[0];
    const todayAppointments = schedule.filter(appt => appt.date === today);
    const upcomingAppointments = schedule.filter(appt => appt.date > today);

    if (loading) return (
        <div className="loading-container">
            <div className="spinner"></div>
            <p>Loading your schedule...</p>
        </div>
    );

    return (
        <div className="doctors-page">
            <div className="page-header">
                <div className="header-content">
                    <div>
                        <h2>👋 Welcome, Dr. {user.username || user.name}</h2>
                        <p style={{ color: 'var(--gray-500)', marginTop: '5px' }}>Here is your daily overview.</p>
                    </div>
                    <div className="stats-summary">
                        <span className="stat-badge">
                            <strong>{todayAppointments.length}</strong> Patients Today
                        </span>
                        <span className="stat-badge" style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' }}>
                            <strong>{upcomingAppointments.length}</strong> Upcoming
                        </span>
                    </div>
                </div>
            </div>

            <div className="dashboard-grid">
                {/* Today's Schedule */}
                <div className="table-container">
                    <div style={{ padding: '20px', borderBottom: '1px solid #eee' }}>
                        <h3 style={{ margin: 0, color: '#2c3e50' }}>📅 Today's Schedule</h3>
                    </div>
                    {todayAppointments.length > 0 ? (
                        <table className="doctors-table">
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th>Patient</th>
                                    <th>Reason</th>
                                    <th>Status</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {todayAppointments.map(appt => (
                                    <tr key={appt.id}>
                                        <td className="time-cell" style={{ fontWeight: 'bold', color: '#4A90A4' }}>{appt.time}</td>
                                        <td className="name-cell">
                                            <div className="doctor-name">
                                                <span className="name-icon">👤</span>
                                                <strong>{appt.patient_name}</strong>
                                            </div>
                                        </td>
                                        <td>{appt.reason}</td>
                                        <td>
                                            <span className={`status-badge ${appt.status}`}>
                                                {appt.status}
                                            </span>
                                        </td>
                                        <td>
                                            <button className="action-btn view-btn" title="View Details">👁️</button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    ) : (
                        <div className="no-results" style={{ padding: '40px' }}>
                            <div style={{ fontSize: '40px', marginBottom: '10px' }}>☕</div>
                            <p>No appointments for today. Enjoy your coffee!</p>
                        </div>
                    )}
                </div>

                {/* Upcoming Schedule */}
                <div className="table-container" style={{ marginTop: '30px' }}>
                    <div style={{ padding: '20px', borderBottom: '1px solid #eee' }}>
                        <h3 style={{ margin: 0, color: '#2c3e50' }}>🗓️ Upcoming Appointments</h3>
                    </div>
                    {upcomingAppointments.length > 0 ? (
                        <table className="doctors-table">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Time</th>
                                    <th>Patient</th>
                                    <th>Reason</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {upcomingAppointments.map(appt => (
                                    <tr key={appt.id}>
                                        <td style={{ fontWeight: '500' }}>{new Date(appt.date).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })}</td>
                                        <td>{appt.time}</td>
                                        <td className="name-cell">
                                            <div className="doctor-name">
                                                <span className="name-icon">👤</span>
                                                <strong>{appt.patient_name}</strong>
                                            </div>
                                        </td>
                                        <td>{appt.reason}</td>
                                        <td>
                                            <span className={`status-badge ${appt.status}`}>
                                                {appt.status}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    ) : (
                        <div className="no-results" style={{ padding: '40px' }}>
                            <p>No upcoming appointments found.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default DoctorDashboard;
