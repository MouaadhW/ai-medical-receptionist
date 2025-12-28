import React from 'react';
import { Link } from 'react-router-dom';
import './LandingPage.css';

const LandingPage = () => {
    return (
        <div className="landing-page">
            {/* Hero Section */}
            <section className="hero">
                <div className="container">
                    <div className="hero-content">
                        {/* MODIFY LOGO SIZE HERE directly in the style prop */}
                        <img src="/assets/medpulse-logo.png" alt="MedPulse Logo" className="hero-logo" style={{ width: '150px', height: 'auto' }} />
                        <h1 className="hero-title">
                            Welcome to <span className="brand">MedPulse</span>
                        </h1>
                        <p className="hero-subtitle">
                            Revolutionizing Healthcare with AI-Powered Medical Reception
                        </p>
                        <p className="hero-description">
                            Experience 24/7 intelligent medical assistance, seamless appointment scheduling,
                            and expert triage services powered by advanced AI technology.
                        </p>
                        <div className="hero-actions">
                            <Link to="/login" className="btn btn-primary btn-large">
                                Get Started
                            </Link>
                            <Link to="/register" className="btn btn-outline btn-large">
                                Sign Up
                            </Link>
                        </div>
                    </div>
                </div>
            </section>

            {/* Services Section */}
            <section className="services">
                <div className="container">
                    <h2 className="section-title">Our Services</h2>
                    <p className="section-subtitle">
                        Comprehensive medical assistance at your fingertips
                    </p>

                    <div className="services-grid">
                        <div className="service-card">
                            <div className="service-icon">🤖</div>
                            <h3>AI Medical Receptionist</h3>
                            <p>
                                Intelligent virtual receptionist available 24/7 to handle your
                                inquiries, schedule appointments, and provide medical guidance.
                            </p>
                        </div>

                        <div className="service-card">
                            <div className="service-icon">📅</div>
                            <h3>Smart Scheduling</h3>
                            <p>
                                Effortlessly book, reschedule, or cancel appointments with our
                                intelligent scheduling system that works around your availability.
                            </p>
                        </div>

                        <div className="service-card">
                            <div className="service-icon">🩺</div>
                            <h3>Medical Triage</h3>
                            <p>
                                Advanced AI-powered triage system to assess symptoms and prioritize
                                urgent medical needs for timely care.
                            </p>
                        </div>

                        <div className="service-card">
                            <div className="service-icon">🔒</div>
                            <h3>Secure & Private</h3>
                            <p>
                                Your medical data is protected with enterprise-grade security and
                                HIPAA-compliant encryption standards.
                            </p>
                        </div>

                        <div className="service-card">
                            <div className="service-icon">💬</div>
                            <h3>Multi-Channel Support</h3>
                            <p>
                                Connect via phone, web chat, or voice calls - choose the communication
                                method that works best for you.
                            </p>
                        </div>

                        <div className="service-card">
                            <div className="service-icon">📊</div>
                            <h3>Health Dashboard</h3>
                            <p>
                                Track your appointments, view medical history, and manage your
                                health information in one centralized dashboard.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="features">
                <div className="container">
                    <h2 className="section-title">Why Choose MedPulse?</h2>

                    <div className="features-grid">
                        <div className="feature">
                            <div className="feature-number">01</div>
                            <h3>Always Available</h3>
                            <p>24/7 access to medical assistance without wait times or appointments</p>
                        </div>

                        <div className="feature">
                            <div className="feature-number">02</div>
                            <h3>Instant Responses</h3>
                            <p>Get immediate answers to your medical queries and concerns</p>
                        </div>

                        <div className="feature">
                            <div className="feature-number">03</div>
                            <h3>Personalized Care</h3>
                            <p>AI learns your medical history to provide tailored recommendations</p>
                        </div>

                        <div className="feature">
                            <div className="feature-number">04</div>
                            <h3>Cost Effective</h3>
                            <p>Reduce unnecessary visits with accurate preliminary assessments</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="cta">
                <div className="container">
                    <h2>Ready to Experience the Future of Healthcare?</h2>
                    <p>Join thousands of patients who trust MedPulse for their medical needs</p>
                    <Link to="/register" className="btn btn-primary btn-large">
                        Create Your Account
                    </Link>
                </div>
            </section>

            {/* Footer */}
            <footer className="footer">
                <div className="container">
                    <div className="footer-content">
                        <div className="footer-section">
                            <h4>MedPulse</h4>
                            <p>AI-Powered Medical Reception</p>
                        </div>
                        <div className="footer-section">
                            <h4>Quick Links</h4>
                            <Link to="/login">Login</Link>
                            <Link to="/register">Sign Up</Link>
                        </div>
                        <div className="footer-section">
                            <h4>Contact</h4>
                            <p>Email: support@medpulse.com</p>
                            <p>Phone: 1-800-MED-PULSE</p>
                        </div>
                    </div>
                    <div className="footer-bottom">
                        <p>&copy; 2025 MedPulse. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
