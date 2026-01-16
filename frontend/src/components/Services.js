import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function Services() {
    const navigate = useNavigate();

    const plans = [
        {
            name: 'Regular',
            price: '$299',
            period: '/month',
            color: '#64748B',
            gradient: 'linear-gradient(135deg, #64748B, #475569)',
            features: [
                'AI Voice Receptionist',
                'Up to 500 monthly calls',
                'Basic appointment scheduling',
                'Email notifications',
                'Standard support',
                'Patient database (up to 1,000)',
                'Basic analytics dashboard'
            ]
        },
        {
            name: 'Pro',
            price: '$599',
            period: '/month',
            color: '#0891B2',
            gradient: 'linear-gradient(135deg, #0891B2, #4F46E5)',
            featured: true,
            features: [
                'Everything in Regular, plus:',
                'Up to 2,000 monthly calls',
                'Advanced AI scheduling with priorities',
                'SMS & Email notifications',
                'Priority support (24/7)',
                'Unlimited patient database',
                'Advanced analytics & reports',
                'Multi-language support',
                'Custom voice & branding',
                'API access'
            ]
        },
        {
            name: 'Ultimate',
            price: '$999',
            period: '/month',
            color: '#4F46E5',
            gradient: 'linear-gradient(135deg, #4F46E5, #8B5CF6)',
            features: [
                'Everything in Pro, plus:',
                'Unlimited monthly calls',
                'Dedicated AI model training',
                'White-label solution',
                'Custom integrations (EHR/EMR)',
                'Dedicated account manager',
                'On-premise deployment option',
                'Advanced security & compliance',
                'Custom feature development',
                'SLA guarantee (99.9% uptime)'
            ]
        }
    ];

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
                        navigate('/about');
                    }}>
                        About Us
                    </a>
                    <a href="#services" style={{
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

            {/* Header */}
            <div style={{ textAlign: 'center', marginBottom: '3rem', marginTop: '6rem' }}>
                <h1 style={{
                    fontSize: '3.5rem',
                    fontWeight: '800',
                    color: '#0F172A',
                    marginBottom: '1rem'
                }}>
                    Choose Your <span className="text-gradient-teal">Plan</span>
                </h1>
                <p style={{ fontSize: '1.25rem', color: '#475569' }}>
                    Select the perfect plan for your medical practice
                </p>
            </div>

            {/* Pricing Cards */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
                gap: '2rem',
                maxWidth: '1400px',
                margin: '0 auto',
                padding: '0 2rem'
            }}>
                {plans.map((plan, index) => (
                    <div
                        key={index}
                        className="card"
                        style={{
                            padding: '2.5rem',
                            background: plan.featured ? 'rgba(255, 255, 255, 0.98)' : 'rgba(255, 255, 255, 0.9)',
                            border: plan.featured ? '2px solid #0891B2' : '1px solid rgba(0, 0, 0, 0.1)',
                            transform: plan.featured ? 'scale(1.05)' : 'scale(1)',
                            transition: 'all 0.3s ease',
                            position: 'relative',
                            overflow: 'hidden'
                        }}
                    >
                        {plan.featured && (
                            <div style={{
                                position: 'absolute',
                                top: '1rem',
                                right: '1rem',
                                background: plan.gradient,
                                color: 'white',
                                padding: '0.375rem 1rem',
                                borderRadius: '20px',
                                fontSize: '0.75rem',
                                fontWeight: '600'
                            }}>
                                MOST POPULAR
                            </div>
                        )}

                        <h3 style={{
                            fontSize: '1.8rem',
                            fontWeight: '700',
                            color: plan.color,
                            marginBottom: '1rem'
                        }}>
                            {plan.name}
                        </h3>

                        <div style={{ marginBottom: '2rem' }}>
                            <span style={{
                                fontSize: '3rem',
                                fontWeight: '800',
                                background: plan.gradient,
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                backgroundClip: 'text'
                            }}>
                                {plan.price}
                            </span>
                            <span style={{ color: '#64748B', fontSize: '1.1rem' }}>
                                {plan.period}
                            </span>
                        </div>

                        <ul style={{
                            listStyle: 'none',
                            padding: 0,
                            margin: '0 0 2rem 0',
                            color: '#475569'
                        }}>
                            {plan.features.map((feature, idx) => (
                                <li key={idx} style={{
                                    padding: '0.75rem 0',
                                    borderBottom: idx < plan.features.length - 1 ? '1px solid rgba(0, 0, 0, 0.05)' : 'none',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.75rem',
                                    fontSize: '0.95rem',
                                    fontWeight: feature.includes('Everything') ? '600' : '400'
                                }}>
                                    <span style={{
                                        color: plan.color,
                                        fontSize: '1.2rem'
                                    }}>
                                        ✓
                                    </span>
                                    {feature}
                                </li>
                            ))}
                        </ul>

                        <button
                            onClick={() => navigate('/register')}
                            style={{
                                width: '100%',
                                background: plan.gradient,
                                color: 'white',
                                border: 'none',
                                padding: '1rem',
                                borderRadius: '12px',
                                fontSize: '1rem',
                                fontWeight: '600',
                                cursor: 'pointer',
                                transition: 'all 0.2s ease',
                                boxShadow: `0 4px 12px ${plan.color}40`
                            }}
                            onMouseEnter={(e) => {
                                e.target.style.transform = 'translateY(-2px)';
                                e.target.style.boxShadow = `0 6px 20px ${plan.color}60`;
                            }}
                            onMouseLeave={(e) => {
                                e.target.style.transform = 'translateY(0)';
                                e.target.style.boxShadow = `0 4px 12px ${plan.color}40`;
                            }}
                        >
                            Get Started
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}
