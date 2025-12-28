import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import './auth.css';

const Register = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        try {
            const result = await register(username, email, password);
            setSuccess(`Registration successful! Your OTID is: ${result.otid}. Please remember this for verification.`);
            setTimeout(() => navigate('/login'), 3000);
        } catch (err) {
            setError('Registration failed. Username or email might be taken.');
        }
    };

    return (
        <div className="auth-container">
            <div className="card auth-card">
                {/* MODIFY LOGO SIZE HERE directly in the style prop */}
                <img src="/assets/medpulse-logo.png" alt="MedPulse" className="auth-logo" style={{ width: '65px', height: 'auto' }} />
                <h2 className="text-center mb-4">Join MedPulse</h2>
                {error && <div className="alert alert-error">{error}</div>}
                {success && <div className="alert alert-success">{success}</div>}
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="label">Username</label>
                        <input
                            type="text"
                            className="input"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label className="label">Email</label>
                        <input
                            type="email"
                            className="input"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label className="label">Password</label>
                        <input
                            type="password"
                            className="input"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>Register</button>
                </form>
                <p className="text-center" style={{ marginTop: 'var(--space-4)' }}>
                    Already have an account? <Link to="/login" className="text-primary">Login</Link>
                </p>
            </div>
        </div>
    );
};

export default Register;
