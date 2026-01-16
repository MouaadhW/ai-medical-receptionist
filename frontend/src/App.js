import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { AnimatePresence } from 'framer-motion';
import './i18n';
import { AuthProvider, useAuth } from './context/AuthContext';
import LandingPage from './components/LandingPage';
import AboutUs from './components/AboutUs';
import Services from './components/Services';
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
import PulseLedger from './components/billing/PulseLedger';
import NeuralHistory from './components/history/NeuralHistory';
import Sidebar from './components/Sidebar';
import './theme.css';
import './App.css';

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
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

// Separate component to use router hooks
const AppContent = () => {
  const { user } = useAuth();

  return (
    <div className="App">
      {user && <Sidebar />}
      <div className="main-content">
        <AnimatePresence mode="wait">
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<PublicOrDashboard />} />
            <Route path="/about" element={<AboutUs />} />
            <Route path="/services" element={<Services />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected Dashboard Route */}
            <Route
              path="/dashboard"
              element={
                <RequireAuth>
                  <div className="page-transition">
                    <RoleBasedDashboard />
                  </div>
                </RequireAuth>
              }
            />

            {/* Admin Routes */}
            <Route
              path="/patients"
              element={
                <RequireAuth role="admin">
                  <div className="page-transition">
                    <Patients />
                  </div>
                </RequireAuth>
              }
            />
            <Route
              path="/doctors"
              element={
                <RequireAuth role="admin">
                  <div className="page-transition">
                    <Doctors />
                  </div>
                </RequireAuth>
              }
            />
            <Route
              path="/appointments"
              element={
                <RequireAuth role="admin">
                  <div className="page-transition">
                    <Appointments />
                  </div>
                </RequireAuth>
              }
            />
            <Route
              path="/calls"
              element={
                <RequireAuth role="admin">
                  <div className="page-transition">
                    <Calls />
                  </div>
                </RequireAuth>
              }
            />

            {/* Shared/Test Routes */}
            <Route
              path="/phone"
              element={
                <RequireAuth>
                  <div className="page-transition">
                    <PhoneInterface />
                  </div>
                </RequireAuth>
              }
            />
            <Route
              path="/chat"
              element={
                <RequireAuth>
                  <div className="page-transition">
                    <ChatInterface />
                  </div>
                </RequireAuth>
              }
            />

            {/* Patient-Centric Modules */}
            <Route
              path="/billing"
              element={
                <RequireAuth>
                  <div className="page-transition">
                    <PulseLedger />
                  </div>
                </RequireAuth>
              }
            />
            <Route
              path="/history"
              element={
                <RequireAuth>
                  <div className="page-transition">
                    <NeuralHistory />
                  </div>
                </RequireAuth>
              }
            />
          </Routes>
        </AnimatePresence>
      </div>
    </div>
  );
};

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
