import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from 'react-i18next';
import './Sidebar.css';

const Sidebar = () => {
    const [isCollapsed, setIsCollapsed] = useState(false);
    const { user, logout } = useAuth();
    const { t, i18n } = useTranslation();
    const location = useLocation();

    if (!user) return null;

    const toggleSidebar = () => setIsCollapsed(!isCollapsed);

    const toggleLanguage = () => {
        i18n.changeLanguage(i18n.language === 'en' ? 'fr' : 'en');
    };

    const navItems = [
        { path: '/dashboard', icon: '📊', label: t('dashboard'), roles: ['admin', 'doctor', 'user'] },
        { path: '/doctors', icon: '👨‍⚕️', label: t('doctors'), roles: ['admin'] },
        { path: '/patients', icon: '🏥', label: t('active_patients'), roles: ['admin'] },
        { path: '/appointments', icon: '📅', label: t('total_appointments'), roles: ['admin'] },
        { path: '/calls', icon: '📞', label: t('calls'), roles: ['admin'] },
        { path: '/history', icon: '🧠', label: 'Medical History', roles: ['admin', 'doctor', 'user'] },
        { path: '/billing', icon: '💰', label: 'Billing', roles: ['admin', 'doctor', 'user'] },
        { path: '/phone', icon: '🎙️', label: t('voice_test'), roles: ['admin', 'user'] },
        { path: '/chat', icon: '💬', label: 'Chat', roles: ['admin', 'user'] },
    ];

    // Filter items based on user role
    const filteredItems = navItems.filter(item => item.roles.includes(user.role));

    const sidebarVariants = {
        expanded: { width: '260px' },
        collapsed: { width: '80px' }
    };

    return (
        <motion.nav
            className={`sidebar glass ${isCollapsed ? 'collapsed' : ''}`}
            initial="expanded"
            animate={isCollapsed ? "collapsed" : "expanded"}
            variants={sidebarVariants}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
        >
            {/* Header */}
            <div className="sidebar-header">
                <motion.div
                    className="logo-container"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                >
                    <img src="/assets/medpulse-logo.png" alt="Logo" className="sidebar-logo" />
                    <AnimatePresence>
                        {!isCollapsed && (
                            <motion.h1
                                className="brand-name"
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -10 }}
                            >
                                MedPulse
                            </motion.h1>
                        )}
                    </AnimatePresence>
                </motion.div>

                <button className="collapse-btn" onClick={toggleSidebar}>
                    {isCollapsed ? '›' : '‹'}
                </button>
            </div>

            {/* User Info */}
            <div className="user-profile">
                <div className="avatar-placeholder glow-teal">
                    {user.username.charAt(0).toUpperCase()}
                </div>
                {!isCollapsed && (
                    <div className="user-details">
                        <span className="user-name">{user.username}</span>
                        <span className="user-role badge badge-info">{user.role}</span>
                    </div>
                )}
            </div>

            {/* Navigation Links */}
            <div className="nav-menu">
                {filteredItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) =>
                            `nav-item ${isActive ? 'active glow-teal' : ''}`
                        }
                    >
                        <span className="nav-icon">{item.icon}</span>
                        <AnimatePresence>
                            {!isCollapsed && (
                                <motion.span
                                    className="nav-label"
                                    initial={{ opacity: 0, width: 0 }}
                                    animate={{ opacity: 1, width: 'auto' }}
                                    exit={{ opacity: 0, width: 0 }}
                                >
                                    {item.label}
                                </motion.span>
                            )}
                        </AnimatePresence>

                        {/* Active Indicator Line */}
                        {location.pathname === item.path && (
                            <motion.div
                                className="active-indicator"
                                layoutId="activeIndicator"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                            />
                        )}
                    </NavLink>
                ))}
            </div>

            {/* Footer Controls */}
            <div className="sidebar-footer">
                <button onClick={toggleLanguage} className="footer-btn" title="Toggle Language">
                    {isCollapsed ? (i18n.language === 'en' ? '🇺🇸' : '🇫🇷') : (i18n.language === 'en' ? '🇺🇸 EN' : '🇫🇷 FR')}
                </button>
                <button onClick={logout} className="footer-btn logout" title="Logout">
                    {isCollapsed ? '🚪' : '🚪 Logout'}
                </button>
            </div>
        </motion.nav>
    );
};

export default Sidebar;
