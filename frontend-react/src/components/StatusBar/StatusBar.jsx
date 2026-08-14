import React from 'react';
import './StatusBar.css';

function StatusBar({ loading, error, onReset, isConnected }) {
  return (
    <div className="status-bar">
      <div className="status-left">
        {loading && <span className="status-indicator loading">⏳ Connexion...</span>}
        {error && <span className="status-indicator error">⚠️ {error}</span>}
        {isConnected && <span className="status-indicator ok">✅ Connecté</span>}
      </div>
      <button className="btn-reset" onClick={onReset}>🔄 Reset</button>
    </div>
  );
}

export default StatusBar;