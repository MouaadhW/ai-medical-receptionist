import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Doctors.css'; // Assuming you have a CSS file for this component
import { API_BASE_URL } from '../config';

const APIURL = API_BASE_URL;

const Doctors = () => {
    const [doctors, setDoctors] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [showCreateForm, setShowCreateForm] = useState(false);

    useEffect(() => {
        fetchDoctors();
    }, []);

    const fetchDoctors = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(`${APIURL}/doctors`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setDoctors(response.data);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching doctors:', error);
            setLoading(false);
        }
    };

    const filteredDoctors = doctors.filter(doc =>
        doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.specialty.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="doctors-page">
            <div className="page-header">
                <div className="header-content">
                    <h2>👨‍⚕️ Doctor Records</h2>
                    <div className="stats-summary">
                        <span className="stat-badge">
                            <strong>{doctors.length}</strong> Total Doctors
                        </span>
                        <span className="stat-badge">
                            <strong>{filteredDoctors.length}</strong> {searchTerm ? 'Filtered' : 'Showing'}
                        </span>
                    </div>
                </div>

                <div className="search-container">
                    <input
                        type="text"
                        placeholder="🔍 Search by name or specialty..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="search-input"
                    />
                    {searchTerm && (
                        <button className="clear-btn" onClick={() => setSearchTerm('')}>✕</button>
                    )}
                </div>
            </div>

            {/* Collapsible Create Form */}
            <div style={{ marginBottom: '20px' }}>
                <AdminDoctorManager onSuccess={fetchDoctors} />
            </div>

            {loading ? (
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Loading doctors...</p>
                </div>
            ) : filteredDoctors.length === 0 ? (
                <div className="no-results">
                    <div className="no-results-icon">🔍</div>
                    <h3>No doctors found</h3>
                    <p>No doctors match "{searchTerm}"</p>
                </div>
            ) : (
                <div className="table-container">
                    <table className="doctors-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Specialty</th>
                                <th>Contact</th>
                                <th>Username</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredDoctors.map((doc) => (
                                <tr key={doc.id}>
                                    <td className="id-cell">
                                        <span className="doctor-id">#{doc.id}</span>
                                    </td>
                                    <td className="name-cell">
                                        <div className="doctor-name">
                                            <span className="name-icon">👨‍⚕️</span>
                                            <strong>{doc.name}</strong>
                                        </div>
                                    </td>
                                    <td>
                                        <span className="specialty-badge">{doc.specialty}</span>
                                    </td>
                                    <td>
                                        <div>📞 {doc.phone}</div>
                                        <div style={{ fontSize: '0.8rem', color: '#888' }}>{doc.email}</div>
                                    </td>
                                    <td>
                                        <code>{doc.username}</code>
                                    </td>
                                    <td className="actions-cell">
                                        <button className="action-btn edit-btn" title="Edit">✏️</button>
                                        <button className="action-btn view-btn" title="View Schedule">📅</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default Doctors;
