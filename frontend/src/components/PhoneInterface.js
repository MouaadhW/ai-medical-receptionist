import React, { useEffect } from 'react';
import './PhoneInterface.css';

function PhoneInterface() {
  useEffect(() => {
    // Automatically redirect to voice server
    window.location.href = 'http://localhost:8003';
  }, []);

  return (
    <div className="phone-interface">
      <div className="phone-container">
        <div className="phone-header">
          <h2>📞 Redirecting to Voice Interface...</h2>
          <p>Please wait while we connect you to the AI Medical Receptionist</p>
        </div>

        <div className="phone-body">
          <div className="phone-screen">
            <div className="phone-icon">🏥</div>
            <h3>AI Medical Receptionist</h3>
            <p className="phone-status">Connecting...</p>
          </div>

          <div className="phone-info">
            <h4>💡 If not redirected automatically:</h4>
            <a
              href="http://localhost:8003"
              className="manual-link"
              target="_blank"
              rel="noopener noreferrer"
            >
              Click here to open Voice Interface
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PhoneInterface;
