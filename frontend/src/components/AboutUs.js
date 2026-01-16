import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function AboutUs() {
    const navigate = useNavigate();

    return (
        <div style={{
            minHeight: '100vh',
            background: 'linear-gradient(135deg, #F8FAFC 0%, #E0F2FE 100%)',
            padding: '2rem'
        }}>
            {/* Floating Curved Navbar */}
            <nav style={{
                position: 'fixed',
                top: '2rem',
                left: '50%',
                transform: 'translateX(-50%)',
                zIndex: 1000,
                background: 'rgba(255, 255, 255, 0.95)',
                backdropFilter: 'blur(20px)',
                WebkitBackdropFilter: 'blur(20px)',
                borderRadius: '50px',
                padding: '1.5rem 3rem',
                display: 'flex',
                alignItems: 'center',
                gap: '3rem',
                minWidth: '900px',
                boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.05)',
                border: '1px solid rgba(8, 145, 178, 0.2)',
            }}>
                <div style={{
                    fontSize: '1.4rem',
                    fontWeight: '700',
                    color: '#0891B2',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    cursor: 'pointer',
                    whiteSpace: 'nowrap'
                }} onClick={() => navigate('/')}>
                    <span style={{
                        width: '10px',
                        height: '10px',
                        background: '#0891B2',
                        borderRadius: '50%',
                        boxShadow: '0 0 10px rgba(8, 145, 178, 0.5)'
                    }}></span>
                    MedPulse
                </div>

                <div style={{ display: 'flex', gap: '2rem', alignItems: 'center', flex: 1, justifyContent: 'center' }}>
                    <a href="#home" style={{
                        color: '#475569',
                        textDecoration: 'none',
                        fontSize: '1rem',
                        fontWeight: '500',
                        transition: 'all 0.2s ease',
                        padding: '0.5rem 1.25rem',
                        borderRadius: '20px',
                        whiteSpace: 'nowrap'
                    }} onMouseEnter={(e) => {
                        e.target.style.color = '#0891B2';
                        e.target.style.background = 'rgba(8, 145, 178, 0.1)';
                    }} onMouseLeave={(e) => {
                        e.target.style.color = '#475569';
                        e.target.style.background = 'transparent';
                    }} onClick={(e) => {
                        e.preventDefault();
                        navigate('/');
                    }}>
                        Home
                    </a>
                    <a href="#about" style={{
                        color: '#0891B2',
                        textDecoration: 'none',
                        fontSize: '1rem',
                        fontWeight: '600',
                        transition: 'all 0.2s ease',
                        padding: '0.5rem 1.25rem',
                        borderRadius: '20px',
                        whiteSpace: 'nowrap',
                        background: 'rgba(8, 145, 178, 0.1)'
                    }}>
                        About Us
                    </a>
                    <a href="#services" style={{
                        color: '#475569',
                        textDecoration: 'none',
                        fontSize: '1rem',
                        fontWeight: '500',
                        transition: 'all 0.2s ease',
                        padding: '0.5rem 1.25rem',
                        borderRadius: '20px',
                        whiteSpace: 'nowrap'
                    }} onMouseEnter={(e) => {
                        e.target.style.color = '#0891B2';
                        e.target.style.background = 'rgba(8, 145, 178, 0.1)';
                    }} onMouseLeave={(e) => {
                        e.target.style.color = '#475569';
                        e.target.style.background = 'transparent';
                    }} onClick={(e) => {
                        e.preventDefault();
                        navigate('/services');
                    }}>
                        Services
                    </a>
                </div>

                <button
                    onClick={() => navigate('/login')}
                    style={{
                        background: 'linear-gradient(135deg, #0891B2, #4F46E5)',
                        color: 'white',
                        border: 'none',
                        padding: '0.75rem 2rem',
                        borderRadius: '25px',
                        fontSize: '1rem',
                        fontWeight: '600',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        boxShadow: '0 4px 12px rgba(8, 145, 178, 0.3)',
                        whiteSpace: 'nowrap'
                    }}
                    onMouseEnter={(e) => {
                        e.target.style.transform = 'translateY(-2px)';
                        e.target.style.boxShadow = '0 6px 20px rgba(8, 145, 178, 0.4)';
                    }}
                    onMouseLeave={(e) => {
                        e.target.style.transform = 'translateY(0)';
                        e.target.style.boxShadow = '0 4px 12px rgba(8, 145, 178, 0.3)';
                    }}
                >
                    Login / Sign Up
                </button>
            </nav>

            {/* Content */}
            <div className="glass-medium" style={{
                maxWidth: '1200px',
                margin: '6rem auto 0',
                padding: '4rem',
                borderRadius: '24px',
                boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
            }}>
                <h1 style={{
                    fontSize: '3rem',
                    fontWeight: '800',
                    color: '#0F172A',
                    marginBottom: '2rem',
                    textAlign: 'center'
                }}>
                    About <span className="text-gradient-teal">MedPulse</span>
                </h1>

                <div style={{
                    display: 'grid',
                    gap: '2rem',
                    color: '#475569',
                    fontSize: '1.1rem',
                    lineHeight: '1.8'
                }}>
                    <section>
                        <h2 style={{ color: '#0891B2', fontSize: '1.8rem', marginBottom: '1rem' }}>
                            Our Mission
                        </h2>
                        <p>
                            MedPulse is revolutionizing healthcare administration with cutting-edge AI technology.
                            Our intelligent receptionist system streamlines patient interactions, automates appointment
                            management, and enhances the overall healthcare experience for both providers and patients.
                        </p>
                    </section>

                    <section>
                        <h2 style={{ color: '#0891B2', fontSize: '1.8rem', marginBottom: '1rem' }}>
                            What We Do
                        </h2>
                        <div style={{ display: 'grid', gap: '1rem' }}>
                            <div className="card" style={{ padding: '1.5rem' }}>
                                <h3 style={{ color: '#0F172A', fontSize: '1.3rem', marginBottom: '0.5rem' }}>
                                    🤖 AI-Powered Assistance
                                </h3>
                                <p>
                                    Our advanced AI handles patient inquiries, schedules appointments, and provides
                                    24/7 support using natural language processing.
                                </p>
                            </div>
                            <div className="card" style={{ padding: '1.5rem' }}>
                                <h3 style={{ color: '#0F172A', fontSize: '1.3rem', marginBottom: '0.5rem' }}>
                                    📅 Smart Scheduling
                                </h3>
                                <p>
                                    Intelligent appointment management that considers doctor availability, patient
                                    preferences, and emergency priorities automatically.
                                </p>
                            </div>
                            <div className="card" style={{ padding: '1.5rem' }}>
                                <h3 style={{ color: '#0F172A', fontSize: '1.3rem', marginBottom: '0.5rem' }}>
                                    📊 Data Analytics
                                </h3>
                                <p>
                                    Comprehensive insights into patient flow, appointment trends, and operational
                                    efficiency to help optimize your practice.
                                </p>
                            </div>
                        </div>
                    </section>

                    <section>
                        <h2 style={{ color: '#0891B2', fontSize: '1.8rem', marginBottom: '1rem' }}>
                            Why Choose Us
                        </h2>
                        <p>
                            With years of healthcare technology experience, we understand the unique challenges
                            medical practices face. MedPulse combines innovative AI with practical healthcare
                            workflows to deliver a solution that truly makes a difference in day-to-day operations.
                        </p>
                    </section>
                </div>
            </div>
        </div>
    );
}
