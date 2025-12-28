import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './AdminAppointmentManager.css';

const API_URL = 'http://localhost:8000/api';

const AdminAppointmentManager = () => {
    const [appointments, setAppointments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [editingId, setEditingId] = useState(null);
    const [editForm, setEditForm] = useState({});
    const [deleteConfirm, setDeleteConfirm] = useState(null);

    useEffect(() => {
        fetchAppointments();
    }, []);

    const fetchAppointments = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get(`${API_URL}/admin/appointments/all`, {
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

    const handleEdit = (appt) => {
        setEditingId(appt.id);
        setEditForm({
            appointment_date: appt.appointment_date,
            appointment_time: appt.appointment_time,
            status: appt.status,
            notes: appt.notes || ''
        });
    };

    const handleSave = async (id) => {
        try {
            const token = localStorage.getItem('token');
            await axios.put(`${API_URL}/admin/appointments/${id}`, editForm, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setEditingId(null);
            fetchAppointments();
        } catch (err) {
            alert('Failed to update appointment');
            console.error(err);
        }
    };

    const handleDelete = async (id) => {
        try {
            const token = localStorage.getItem('token');
            await axios.delete(`${API_URL}/admin/appointments/${id}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setDeleteConfirm(null);
            fetchAppointments();
        } catch (err) {
            alert('Failed to delete appointment');
            console.error(err);
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
        <div className="admin-appointment-manager">
            <h3>Appointment Management</h3>

            {appointments.length === 0 ? (
                <p className="text-muted">No appointments found</p>
            ) : (
                <div className="appointments-table">
                    <table>
                        <thead>
                            <tr>
                                <th>User</th>
                                <th>Doctor</th>
                                <th>Specialty</th>
                                <th>Date</th>
                                <th>Time</th>
                                <th>Status</th>
                                <th>Reason</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {appointments.map((appt) => (
                                <tr key={appt.id}>
                                    <td>
                                        <div className="user-cell">
                                            <strong>{appt.user_name}</strong>
                                            <small>{appt.user_email}</small>
                                        </div>
                                    </td>
                                    <td>{appt.doctor_name}</td>
                                    <td><span className="specialty-tag">{appt.specialty}</span></td>
                                    <td>
                                        {editingId === appt.id ? (
                                            <input
                                                type="date"
                                                value={editForm.appointment_date}
                                                onChange={(e) => setEditForm({ ...editForm, appointment_date: e.target.value })}
                                            />
                                        ) : (
                                            new Date(appt.appointment_date).toLocaleDateString()
                                        )}
                                    </td>
                                    <td>
                                        {editingId === appt.id ? (
                                            <input
                                                type="time"
                                                value={editForm.appointment_time}
                                                onChange={(e) => setEditForm({ ...editForm, appointment_time: e.target.value })}
                                            />
                                        ) : (
                                            appt.appointment_time
                                        )}
                                    </td>
                                    <td>
                                        {editingId === appt.id ? (
                                            <select
                                                value={editForm.status}
                                                onChange={(e) => setEditForm({ ...editForm, status: e.target.value })}
                                            >
                                                <option value="scheduled">Scheduled</option>
                                                <option value="completed">Completed</option>
                                                <option value="cancelled">Cancelled</option>
                                            </select>
                                        ) : (
                                            <span className={`status-badge ${getStatusClass(appt.status)}`}>
                                                {appt.status}
                                            </span>
                                        )}
                                    </td>
                                    <td>{appt.reason}</td>
                                    <td>
                                        <div className="action-buttons">
                                            {editingId === appt.id ? (
                                                <>
                                                    <button
                                                        className="btn-save"
                                                        onClick={() => handleSave(appt.id)}
                                                    >
                                                        ✓ Save
                                                    </button>
                                                    <button
                                                        className="btn-cancel"
                                                        onClick={() => setEditingId(null)}
                                                    >
                                                        ✗ Cancel
                                                    </button>
                                                </>
                                            ) : (
                                                <>
                                                    <button
                                                        className="btn-edit"
                                                        onClick={() => handleEdit(appt)}
                                                    >
                                                        ✎ Edit
                                                    </button>
                                                    <button
                                                        className="btn-delete"
                                                        onClick={() => setDeleteConfirm(appt.id)}
                                                    >
                                                        🗑 Delete
                                                    </button>
                                                </>
                                            )}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Delete Confirmation Modal */}
            {deleteConfirm && (
                <div className="modal-overlay" onClick={() => setDeleteConfirm(null)}>
                    <div className="modal" onClick={(e) => e.stopPropagation()}>
                        <h3>Confirm Delete</h3>
                        <p>Are you sure you want to delete this appointment?</p>
                        <div className="modal-actions">
                            <button
                                className="btn btn-secondary"
                                onClick={() => setDeleteConfirm(null)}
                            >
                                Cancel
                            </button>
                            <button
                                className="btn btn-primary"
                                onClick={() => handleDelete(deleteConfirm)}
                                style={{ background: 'var(--error)' }}
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AdminAppointmentManager;
