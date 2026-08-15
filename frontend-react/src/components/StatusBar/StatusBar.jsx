import React from 'react';
import './StatusBar.css';

function StatusBar({ loading, error, onReset, isConnected, powerLed }) {
  return (
    <div className="status-bar">
      <div className="status-left">
        {loading && <span className="status-indicator loading">⏳ Connexion...</span>}
        {error && <span className="status-indicator error">⚠️ {error}</span>}
        {isConnected && <span className="status-indicator ok">✅ Connecté</span>}
        {!isConnected && !loading && !error && <span className="status-indicator offline">⛔ Déconnecté</span>}
      </div>
      <div className="status-right">
        <span className="status-led">
          <span className={`led-small ${powerLed ? 'on' : 'off'}`}></span>
          POWER
        </span>
        <button className="btn-reset" onClick={onReset}>🔄 Reset</button>
      </div>
    </div>
  );
}

export default StatusBar;