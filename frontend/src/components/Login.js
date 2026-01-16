import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import './auth.css';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            await login(username, password);
            navigate('/dashboard');
        } catch (err) {
            setError('Invalid credentials');
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-wrapper" style={{ width: '100%', maxWidth: '420px' }}>
                <Link to="/" className="btn-back">
                    &larr; Back to Home
                </Link>
                <div className="card auth-card">
                    <img src="/assets/medpulse-logo.png" alt="MedPulse" className="auth-logo" style={{ width: '80px', height: 'auto', marginBottom: '1.5rem' }} />
                    <h2 className="text-center mb-4">Welcome to MedPulse</h2>
                    {error && <div className="alert alert-error">{error}</div>}
                    <form onSubmit={handleSubmit} autoComplete="off">
                        <div className="form-group">
                            <label className="label" htmlFor="username">Username</label>
                            <input
                                id="username"
                                name="username"
                                type="text"
                                className="input"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                                autoComplete="off"
                                data-lpignore="true"
                            />
                        </div>
                        <div className="form-group">
                            <label className="label" htmlFor="password">Password</label>
                            <input
                                id="password"
                                name="password"
                                type="password"
                                className="input"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                autoComplete="new-password"
                                data-lpignore="true"
                            />
                        </div>
                        <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>Login</button>
                    </form>
                    <p className="text-center" style={{ marginTop: 'var(--spacing-md)' }}>
                        Don't have an account? <Link to="/register" className="text-primary">Register</Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Login;
