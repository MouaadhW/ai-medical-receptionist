import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Patients.css';

function Patients() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      const response = await axios.get('/api/patients');
      setPatients(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching patients:', error);
      setLoading(false);
    }
  };

  const filteredPatients = patients.filter(patient =>
    patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.phone.includes(searchTerm)
  );

  const calculateAge = (dob) => {
    if (!dob) return 'N/A';
    const birthDate = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading patients...</p>
      </div>
    );
  }

  return (
    <div className="patients-page">
      <div className="page-header">
        <div className="header-content">
          <h2>👥 Patient Records</h2>
          <div className="stats-summary">
            <span className="stat-badge">
              <strong>{patients.length}</strong> Total Patients
            </span>
            <span className="stat-badge">
              <strong>{filteredPatients.length}</strong> {searchTerm ? 'Filtered' : 'Showing'}
            </span>
          </div>
        </div>

        <div className="search-container">
          <input
            type="text"
            placeholder="🔍 Search by name or phone..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          {searchTerm && (
            <button
              className="clear-btn"
              onClick={() => setSearchTerm('')}
              title="Clear search"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {filteredPatients.length === 0 ? (
        <div className="no-results">
          <div className="no-results-icon">🔍</div>
          <h3>No patients found</h3>
          <p>No patients match "{searchTerm}"</p>
        </div>
      ) : (
        <div className="table-container">
          <table className="patients-table">
            <thead>
              <tr>
                <th>Patient ID</th>
                <th>Name</th>
                <th>Phone</th>
                <th>Email</th>
                <th>Date of Birth</th>
                <th>Age</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredPatients.map((patient) => (
                <tr key={patient.id}>
                  <td className="id-cell">
                    <span className="patient-id">#{patient.id}</span>
                  </td>
                  <td className="name-cell">
                    <div className="patient-name">
                      <span className="name-icon">👤</span>
                      <strong>{patient.name}</strong>
                    </div>
                  </td>
                  <td className="phone-cell">
                    <a href={`tel:${patient.phone}`} className="phone-link">
                      📞 {patient.phone}
                    </a>
                  </td>
                  <td className="email-cell">
                    {patient.email ? (
                      <a href={`mailto:${patient.email}`} className="email-link">
                        📧 {patient.email}
                      </a>
                    ) : (
                      <span className="no-data">—</span>
                    )}
                  </td>
                  <td className="dob-cell">
                    {patient.dateofbirth ? (
                      new Date(patient.dateofbirth).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                      })
                    ) : (
                      <span className="no-data">—</span>
                    )}
                  </td>
                  <td className="age-cell">
                    <span className="age-badge">
                      {calculateAge(patient.dateofbirth)} {calculateAge(patient.dateofbirth) !== 'N/A' ? 'yrs' : ''}
                    </span>
                  </td>
                  <td className="actions-cell">
                    <button className="action-btn view-btn" title="View Details">
                      👁️
                    </button>
                    <button className="action-btn edit-btn" title="Edit">
                      ✏️
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

export default Patients;
