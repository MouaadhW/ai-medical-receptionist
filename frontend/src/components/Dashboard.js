import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import AdminAppointmentManager from './AdminAppointmentManager';
import AdminDoctorManager from './AdminDoctorManager';
import './Dashboard.css';

const APIURL = process.env.REACTAPPAPIURL || '/api';

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00c9ff', '#92fe9d'];

function Dashboard() {
  const [analytics, setAnalytics] = useState(null);
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${APIURL}/analytics`);
      setAnalytics(response.data);
      setLoading(false);
      setError(null);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      setError('Failed to load analytics. Make sure the backend is running on port 8000.');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error">
        <div className="error-icon">⚠️</div>
        <h3>Connection Error</h3>
        <p>{error}</p>
        <button className="retry-btn" onClick={fetchAnalytics}>
          🔄 Retry
        </button>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="error">
        <div className="error-icon">📊</div>
        <h3>No Data Available</h3>
        <p>Unable to load analytics data</p>
      </div>
    );
  }

  // Prepare intent distribution data
  const intentData = analytics.intentdistribution
    ? Object.entries(analytics.intentdistribution).map(([name, value]) => ({
      name: name.replace(/_/g, ' ').toUpperCase(),
      value: value
    }))
    : [];

  // Prepare call statistics data
  const callStatsData = [
    { name: 'Total', value: analytics.calls?.total || 0 },
    { name: 'This Week', value: analytics.calls?.week || 0 },
    { name: 'Today', value: analytics.calls?.today || 0 },
    { name: 'Emergency', value: analytics.calls?.emergency || 0 }
  ];

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2 className="page-title">📊 {t('dashboard')}</h2>
        <button className="refresh-btn" onClick={fetchAnalytics}>
          🔄 Refresh
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <h3>{t('active_patients')}</h3>
            <p className="stat-number">{analytics.patients?.total || 0}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📅</div>
          <div className="stat-content">
            <h3>{t('today_appointments')}</h3>
            <p className="stat-number">{analytics.appointments?.upcoming || 0}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📞</div>
          <div className="stat-content">
            <h3>Calls Today</h3>
            <p className="stat-number">{analytics.calls?.today || 0}</p>
          </div>
        </div>

        <div className="stat-card emergency">
          <div className="stat-icon">🚨</div>
          <div className="stat-content">
            <h3>{t('emergencies')}</h3>
            <p className="stat-number">{analytics.calls?.emergency || 0}</p>
          </div>
        </div>
      </div>

      <AdminDoctorManager />

      <div className="charts-grid">
        {intentData.length > 0 ? (
          <div className="chart-card">
            <h3>📊 Call Intent Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={intentData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {intentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="chart-card">
            <h3>📊 Call Intent Distribution</h3>
            <div className="no-data">
              <p>No call data available yet</p>
            </div>
          </div>
        )}

        <div className="chart-card">
          <h3>📈 Call Statistics</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={callStatsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#667eea" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="info-cards">
        <div className="info-card">
          <h3>📈 System Performance</h3>
          <ul>
            <li>
              Average Call Duration:
              <strong> {analytics.calls?.avg_duration || 0}s</strong>
            </li>
            <li>
              Total Appointments:
              <strong> {analytics.appointments?.total || 0}</strong>
            </li>
            <li>
              Today's Appointments:
              <strong> {analytics.appointments?.today || 0}</strong>
            </li>
            <li>
              Total Calls:
              <strong> {analytics.calls?.total || 0}</strong>
            </li>
          </ul>
        </div>

        <div className="info-card">
          <h3>🎯 Quick Actions</h3>
          <div className="quick-actions">
            <button
              className="action-btn"
              onClick={() => window.location.href = '/phone'}
            >
              📞 Test Voice Call
            </button>
            <button
              className="action-btn"
              onClick={() => window.location.href = '/appointments'}
            >
              📅 View Appointments
            </button>
            <button
              className="action-btn"
              onClick={() => window.location.href = '/calls'}
            >
              📊 View Call Logs
            </button>
            <button
              className="action-btn"
              onClick={() => window.location.href = '/patients'}
            >
              👥 View Patients
            </button>
          </div>
        </div >
      </div >

      <AdminAppointmentManager />

      <div className="system-status">
        <div className="status-indicator">
          <span className="status-dot active"></span>
          <span>System Online</span>
        </div>
        <div className="status-info">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>
    </div >
  );
}

export default Dashboard;