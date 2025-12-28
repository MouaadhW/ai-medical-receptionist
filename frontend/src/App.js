import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LandingPage from './components/LandingPage';
import Dashboard from './components/Dashboard';
import UserDashboard from './components/UserDashboard';
import DoctorDashboard from './components/DoctorDashboard';
import Doctors from './components/Doctors';
import Patients from './components/Patients';
import Appointments from './components/Appointments';
import Calls from './components/Calls';
import PhoneInterface from './components/PhoneInterface';
import ChatInterface from './components/ChatInterface';
import Login from './components/Login';
import Register from './components/Register';
import './theme.css';
import './App.css';

// Navigation Component
const Navbar = () => {
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <nav className="navbar">
      <div className="nav-brand">
        <img src="/assets/medpulse-logo.png" alt="MedPulse" className="nav-logo" />
        <h1>MedPulse</h1>
      </div>
      <div className="nav-links">
        {user.role === 'admin' ? (
          <>
            <Link to="/dashboard" className="nav-link">Dashboard</Link>
            <Link to="/doctors" className="nav-link">Doctors</Link>
            <Link to="/patients" className="nav-link">Patients</Link>
            <Link to="/appointments" className="nav-link">Appointments</Link>
            <Link to="/calls" className="nav-link">Calls</Link>
            <Link to="/phone" className="nav-link phone-link">📞 Voice Test</Link>
            <Link to="/chat" className="nav-link chat-link">💬 Chat Test</Link>
          </>
        ) : (
          <>
            <Link to="/dashboard" className="nav-link">Home</Link>
            <Link to="/phone" className="nav-link phone-link">📞 Call Agent</Link>
            <Link to="/chat" className="nav-link chat-link">💬 Chat</Link>
          </>
        )}
        {user.role === 'doctor' && (
          <span className="role-badge">Dt.</span>
        )}
        <button onClick={logout} className="nav-link logout-link">Logout</button>
      </div>
    </nav>
  );
};

// Protected Route Component
const RequireAuth = ({ children, role }) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) return <div className="loading">Loading...</div>;

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (role && user.role !== role) {
    // Redirect to home if unauthorized for specific role
    return <Navigate to="/" replace />;
  }

  return children;
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Navbar />
          <div className="main-content">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<PublicOrDashboard />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              {/* Protected Dashboard Route */}
              <Route
                path="/dashboard"
                element={
                  <RequireAuth>
                    <RoleBasedDashboard />
                  </RequireAuth>
                }
              />

              {/* Admin Routes */}
              <Route
                path="/patients"
                element={
                  <RequireAuth role="admin">
                    <Patients />
                  </RequireAuth>
                }
              />
              <Route
                path="/doctors"
                element={
                  <RequireAuth role="admin">
                    <Doctors />
                  </RequireAuth>
                }
              />
              <Route
                path="/appointments"
                element={
                  <RequireAuth role="admin">
                    <Appointments />
                  </RequireAuth>
                }
              />
              <Route
                path="/calls"
                element={
                  <RequireAuth role="admin">
                    <Calls />
                  </RequireAuth>
                }
              />

              {/* Shared/Test Routes */}
              <Route
                path="/phone"
                element={
                  <RequireAuth>
                    <PhoneInterface />
                  </RequireAuth>
                }
              />
              <Route
                path="/chat"
                element={
                  <RequireAuth>
                    <ChatInterface />
                  </RequireAuth>
                }
              />
            </Routes>
          </div>
        </div>
      </Router>
    </AuthProvider>
  );
}

// Helper to show landing page or dashboard
const PublicOrDashboard = () => {
  const { user, loading } = useAuth();

  if (loading) return <div className="spinner"></div>;

  if (!user) {
    return <LandingPage />;
  }

  return <RoleBasedDashboard />;
};

// Helper to switch dashboard
const RoleBasedDashboard = () => {
  const { user } = useAuth();
  if (user.role === 'admin') {
    return <Dashboard />;
  } else if (user.role === 'doctor') {
    return <DoctorDashboard />;
  }
  return <UserDashboard />;
};

export default App;
