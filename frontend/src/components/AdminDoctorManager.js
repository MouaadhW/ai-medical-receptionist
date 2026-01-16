import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Dashboard.css';
import { API_BASE_URL } from '../config';

const AdminDoctorManager = (props) => {
    const [doctors, setDoctors] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const APIURL = API_BASE_URL;

    const [formData, setFormData] = useState({
        name: '',
        username: '',
        email: '',
        password: '',
        specialty: 'General Practice',
        phone: ''
    });
    const [message, setMessage] = useState('');
    const [isExpanded, setIsExpanded] = useState(false);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token');
            await axios.post(`${APIURL}/admin/create-doctor`, formData, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setMessage('Doctor account created successfully!');
            setFormData({
                name: '',
                username: '',
                email: '',
                password: '',
                specialty: 'General Practice',
                phone: ''
            });
            if (props.onSuccess) props.onSuccess();
        } catch (error) {
            setMessage('Error creating doctor: ' + (error.response?.data?.detail || error.message));
        }
    };

    return (
        <div className="dashboard-card full-width" style={{ marginBottom: '2rem' }}>
            <div className="card-header-action" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h3>➕ Add New Doctor</h3>
                    <p style={{ color: 'var(--gray-500)', fontSize: '0.9rem' }}>Register new medical staff to the system.</p>
                </div>
                <button
                    className={`btn ${isExpanded ? 'btn-outline' : 'btn-primary'}`}
                    onClick={() => setIsExpanded(!isExpanded)}
                >
                    {isExpanded ? 'Cancel' : 'Add Doctor'}
                </button>
            </div>

            {isExpanded && (
                <div className="doctor-form-container" style={{ marginTop: '1.5rem', borderTop: '1px solid var(--gray-200)', paddingTop: '1.5rem' }}>
                    {message && (
                        <div className={`alert ${message.includes('Error') ? 'alert-error' : 'alert-success'}`}>
                            {message}
                        </div>
                    )}
                    <form onSubmit={handleSubmit} className="doctor-form">
                        <div className="grid grid-cols-2" style={{ gap: '1.5rem' }}>
                            <div className="form-group">
                                <label className="label">Full Name</label>
                                <input className="input" name="name" value={formData.name} onChange={handleChange} required placeholder="e.g. Dr. Jane Smith" />
                            </div>
                            <div className="form-group">
                                <label className="label">Specialty</label>
                                <select className="input" name="specialty" value={formData.specialty} onChange={handleChange}>
                                    <option>General Practice</option>
                                    <option>Cardiology</option>
                                    <option>Pediatrics</option>
                                    <option>Dermatology</option>
                                    <option>Neurology</option>
                                    <option>Orthopedics</option>
                                    <option>Psychiatry</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label className="label">Email Address</label>
                                <input className="input" name="email" type="email" value={formData.email} onChange={handleChange} required placeholder="doctor@medpulse.com" />
                            </div>
                            <div className="form-group">
                                <label className="label">Phone Number</label>
                                <input className="input" name="phone" value={formData.phone} onChange={handleChange} required placeholder="+1 555 000 0000" />
                            </div>
                            <div className="form-group">
                                <label className="label">Username (Login)</label>
                                <input className="input" name="username" value={formData.username} onChange={handleChange} required />
                            </div>
                            <div className="form-group">
                                <label className="label">Password</label>
                                <input className="input" name="password" type="password" value={formData.password} onChange={handleChange} required />
                            </div>
                        </div>
                        <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'flex-end' }}>
                            <button type="submit" className="btn btn-primary btn-large">
                                Create Account
                            </button>
                        </div>
                    </form>
                </div>
            )}
        </div>
    );
};

export default AdminDoctorManager;
