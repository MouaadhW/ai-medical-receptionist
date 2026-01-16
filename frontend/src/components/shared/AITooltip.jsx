import React, { useState, useRef, useEffect } from 'react';
import './AITooltip.css';

/**
 * AITooltip - Intelligent tooltip with AI-powered content
 * @param {React.ReactNode} trigger - Element that triggers tooltip
 * @param {string|React.ReactNode} content - Tooltip content
 * @param {string} position - 'top', 'bottom', 'left', 'right'
 * @param {boolean} loading - Show loading state
 * @param {number} delay - Delay before showing (ms)
 */
const AITooltip = ({
    trigger,
    content,
    position = 'top',
    loading = false,
    delay = 300,
    children
}) => {
    const [isVisible, setIsVisible] = useState(false);
    const [coords, setCoords] = useState({ x: 0, y: 0 });
    const triggerRef = useRef(null);
    const tooltipRef = useRef(null);
    const timeoutRef = useRef(null);

    const showTooltip = () => {
        timeoutRef.current = setTimeout(() => {
            setIsVisible(true);
            updatePosition();
        }, delay);
    };

    const hideTooltip = () => {
        if (timeoutRef.current) {
            clearTimeout(timeoutRef.current);
        }
        setIsVisible(false);
    };

    const updatePosition = () => {
        if (!triggerRef.current || !tooltipRef.current) return;

        const triggerRect = triggerRef.current.getBoundingClientRect();
        const tooltipRect = tooltipRef.current.getBoundingClientRect();
        const offset = 10;

        let x, y;

        switch (position) {
            case 'top':
                x = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;
                y = triggerRect.top - tooltipRect.height - offset;
                break;
            case 'bottom':
                x = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;
                y = triggerRect.bottom + offset;
                break;
            case 'left':
                x = triggerRect.left - tooltipRect.width - offset;
                y = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
                break;
            case 'right':
                x = triggerRect.right + offset;
                y = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
                break;
            default:
                x = triggerRect.left;
                y = triggerRect.top;
        }

        // Boundary detection
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;

        if (x < 10) x = 10;
        if (y < 10) y = 10;
        if (x + tooltipRect.width > viewportWidth - 10) {
            x = viewportWidth - tooltipRect.width - 10;
        }
        if (y + tooltipRect.height > viewportHeight - 10) {
            y = viewportHeight - tooltipRect.height - 10;
        }

        setCoords({ x, y });
    };

    useEffect(() => {
        return () => {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
        };
    }, []);

    return (
        <div className="ai-tooltip-container">
            <div
                ref={triggerRef}
                onMouseEnter={showTooltip}
                onMouseLeave={hideTooltip}
                className="ai-tooltip-trigger"
            >
                {trigger || children}
            </div>

            {isVisible && (
                <div
                    ref={tooltipRef}
                    className={`ai-tooltip glass-heavy animate-fadeInScale ${position}`}
                    style={{
                        position: 'fixed',
                        left: `${coords.x}px`,
                        top: `${coords.y}px`,
                        zIndex: 10000
                    }}
                >
                    {loading ? (
                        <div className="ai-tooltip-loading">
                            <div className="skeleton" style={{ height: '16px', width: '100%', marginBottom: '8px' }}></div>
                            <div className="skeleton" style={{ height: '16px', width: '80%' }}></div>
                        </div>
                    ) : (
                        <div className="ai-tooltip-content">
                            {content}
                        </div>
                    )}
                    <div className={`ai-tooltip-arrow ${position}`}></div>
                </div>
            )}
        </div>
    );
};

export default AITooltip;
