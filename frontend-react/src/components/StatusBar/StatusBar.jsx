import React from 'react';
import './StatusBar.css';

function StatusBar({ loading, error, onReset }) {
  return (
    <div className="status-bar">
      <div className="status-left">
        {loading && <span className="status-indicator loading">⏳ Chargement...</span>}
        {error && <span className="status-indicator error">⚠️ {error}</span>}
        {!loading && !error && <span className="status-indicator ok">✅ Connecté</span>}
      </div>
      <button className="btn-reset" onClick={onReset}>🔄 Reset</button>
    </div>
  );
}

export default StatusBar;