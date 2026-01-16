import React from 'react';
import './GlassCard.css';

/**
 * GlassCard - Reusable glassmorphism card component for 2026 aesthetic
 * @param {string} variant - 'light', 'medium', or 'heavy' blur intensity
 * @param {boolean} animated - Enable hover animations
 * @param {string} glowColor - Optional glow color on hover
 * @param {string} className - Additional CSS classes
 * @param {React.ReactNode} children - Card content
 */
const GlassCard = ({
    variant = 'medium',
    animated = true,
    glowColor = null,
    className = '',
    children,
    ...props
}) => {
    const variantClass = {
        light: 'glass',
        medium: 'glass-medium',
        heavy: 'glass-heavy'
    }[variant] || 'glass';

    const classes = [
        'glass-card-component',
        variantClass,
        animated && 'glass-card-animated',
        glowColor && `glow-${glowColor}`,
        className
    ].filter(Boolean).join(' ');

    return (
        <div className={classes} {...props}>
            {children}
        </div>
    );
};

export default GlassCard;
