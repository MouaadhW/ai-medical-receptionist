import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './AppointmentHistory.css';
import { API_BASE_URL } from '../config';

const AppointmentHistory = () => {
    const [appointments, setAppointments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const API_URL = API_BASE_URL;

    useEffect(() => {
        fetchAppointments();
    }, []);

    const fetchAppointments = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get(`${API_URL}/my-appointments`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setAppointments(res.data);
        } catch (err) {
            setError('Failed to load appointments');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const getStatusClass = (status) => {
        switch (status) {
            case 'scheduled': return 'status-scheduled';
            case 'completed': return 'status-completed';
            case 'cancelled': return 'status-cancelled';
            default: return '';
        }
    };

    if (loading) return <div className="spinner"></div>;
    if (error) return <div className="alert alert-error">{error}</div>;

    return (
        <div className="appointment-history">
            <h3>Appointment History</h3>
            {appointments.length === 0 ? (
                <p className="text-muted">No appointments yet. Book one via chat or voice!</p>
            ) : (
                <div className="appointments-list">
                    {appointments.map((appt) => (
                        <div key={appt.id} className="appointment-card">
                            <div className="appointment-header">
                                <div>
                                    <h4>{appt.doctor_name}</h4>
                                    <span className="specialty-badge">{appt.specialty}</span>
                                </div>
                                <span className={`status-badge ${getStatusClass(appt.status)}`}>
                                    {appt.status}
                                </span>
                            </div>
                            <div className="appointment-details">
                                <div className="detail-row">
                                    <span className="icon">📅</span>
                                    <strong>Date:</strong> {new Date(appt.appointment_date).toLocaleDateString()}
                                </div>
                                <div className="detail-row">
                                    <span className="icon">🕐</span>
                                    <strong>Time:</strong> {appt.appointment_time}
                                </div>
                                {appt.reason && (
                                    <div className="detail-row">
                                        <span className="icon">📝</span>
                                        <strong>Reason:</strong> {appt.reason}
                                    </div>
                                )}
                                {appt.notes && (
                                    <div className="detail-row notes">
                                        <span className="icon">💬</span>
                                        <strong>Notes:</strong> {appt.notes}
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default AppointmentHistory;
