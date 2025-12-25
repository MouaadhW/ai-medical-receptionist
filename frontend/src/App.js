import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Patients from './components/Patients';
import Appointments from './components/Appointments';
import Calls from './components/Calls';
import PhoneInterface from './components/PhoneInterface';
import ChatInterface from './components/ChatInterface';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <div className="nav-brand">
            <span className="nav-icon">🏥</span>
            <h1>AI Medical Receptionist</h1>
          </div>
          <div className="nav-links">
            <Link to="/" className="nav-link">Dashboard</Link>
            <Link to="/patients" className="nav-link">Patients</Link>
            <Link to="/appointments" className="nav-link">Appointments</Link>
            <Link to="/calls" className="nav-link">Calls</Link>
            <Link to="/phone" className="nav-link phone-link">📞 Voice Test</Link>
            <Link to="/chat" className="nav-link chat-link">💬 Chat Test</Link>
          </div>
        </nav>

        <div className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/patients" element={<Patients />} />
            <Route path="/appointments" element={<Appointments />} />
            <Route path="/calls" element={<Calls />} />
            <Route path="/phone" element={<PhoneInterface />} />
            <Route path="/chat" element={<ChatInterface />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;