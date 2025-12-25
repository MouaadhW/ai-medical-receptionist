import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Appointments.css';

function Appointments() {
    const [appointments, setAppointments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filterStatus, setFilterStatus] = useState('all');

    useEffect(() => {
        fetchAppointments();
    }, []);

    const fetchAppointments = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/appointments/upcoming');
            setAppointments(response.data);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching appointments:', error);
            setLoading(false);
        }
    };

    const getStatusColor = (status) => {
        const colors = {
            'scheduled': '#27ae60',
            'completed': '#3498db',
            'cancelled': '#e74c3c',
            'pending': '#f39c12'
        };
        return colors[status] || '#95a5a6';
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);

        if (date.toDateString() === today.toDateString()) {
            return 'Today';
        } else if (date.toDateString() === tomorrow.toDateString()) {
            return 'Tomorrow';
        }
        return date.toLocaleDateString('en-US', {
            weekday: 'short',
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    };

    const filteredAppointments = filterStatus === 'all'
        ? appointments
        : appointments.filter(apt => apt.status === filterStatus);

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
                <p>Loading appointments...</p>
            </div>
        );
    }

    return (
        <div className="appointments-page">
            <div className="page-header">
                <div className="header-content">
                    <h2>📅 Appointments</h2>
                    <div className="stats-summary">
                        <span className="stat-badge">
                            <strong>{appointments.length}</strong> Total Upcoming
                        </span>
                        <span className="stat-badge">
                            <strong>{filteredAppointments.length}</strong> {filterStatus === 'all' ? 'Showing' : filterStatus.charAt(0).toUpperCase() + filterStatus.slice(1)}
                        </span>
                    </div>
                </div>

                <div className="filter-container">
                    <label>Filter by Status:</label>
                    <select
                        value={filterStatus}
                        onChange={(e) => setFilterStatus(e.target.value)}
                        className="filter-select"
                    >
                        <option value="all">All Statuses</option>
                        <option value="scheduled">Scheduled</option>
                        <option value="completed">Completed</option>
                        <option value="cancelled">Cancelled</option>
                        <option value="pending">Pending</option>
                    </select>
                </div>
            </div>

            {filteredAppointments.length === 0 ? (
                <div className="no-results">
                    <div className="no-results-icon">📅</div>
                    <h3>No appointments found</h3>
                    <p>{filterStatus === 'all' ? 'No upcoming appointments scheduled' : `No ${filterStatus} appointments`}</p>
                </div>
            ) : (
                <div className="table-container">
                    <table className="appointments-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Date</th>
                                <th>Time</th>
                                <th>Patient</th>
                                <th>Doctor</th>
                                <th>Reason</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredAppointments.map((appointment) => (
                                <tr key={appointment.id}>
                                    <td className="id-cell">
                                        <span className="appointment-id">#{appointment.id}</span>
                                    </td>
                                    <td className="date-cell">
                                        <div className="date-info">
                                            <span className="date-icon">📆</span>
                                            <strong>{formatDate(appointment.date)}</strong>
                                        </div>
                                    </td>
                                    <td className="time-cell">
                                        <span className="time-badge">🕐 {appointment.time}</span>
                                    </td>
                                    <td className="patient-cell">
                                        <div className="patient-info">
                                            <span className="patient-icon">👤</span>
                                            {appointment.patientname}
                                        </div>
                                    </td>
                                    <td className="doctor-cell">
                                        <div className="doctor-info">
                                            <span className="doctor-icon">👨‍⚕️</span>
                                            {appointment.doctorname}
                                        </div>
                                    </td>
                                    <td className="reason-cell">
                                        <span className="reason-text">
                                            {appointment.reason || 'Not specified'}
                                        </span>
                                    </td>
                                    <td className="status-cell">
                                        <span
                                            className="status-badge"
                                            style={{
                                                backgroundColor: `${getStatusColor(appointment.status)}20`,
                                                color: getStatusColor(appointment.status),
                                                border: `2px solid ${getStatusColor(appointment.status)}`
                                            }}
                                        >
                                            {appointment.status.toUpperCase()}
                                        </span>
                                    </td>
                                    <td className="actions-cell">
                                        <button className="action-btn view-btn" title="View Details">
                                            👁️
                                        </button>
                                        <button className="action-btn edit-btn" title="Reschedule">
                                            📝
                                        </button>
                                        <button className="action-btn cancel-btn" title="Cancel">
                                            ❌
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}

export default Appointments;
