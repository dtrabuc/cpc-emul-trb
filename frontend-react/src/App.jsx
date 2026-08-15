// src/App.jsx
import React, { useState } from 'react';
import { useEmulator } from './hooks/useEmulator';
import Screen from './components/Screen/Screen';
import Keyboard from './components/Keyboard/Keyboard';
import Datacorder from './components/Datacorder/Datacorder';
import StatusBar from './components/StatusBar/StatusBar';
import SettingsModal from './components/Settings/SettingsModal';
import './App.css';

function App() {
  const { screen, loading, error, powerLed, isResetting, sendKey, reset, isConnected } = useEmulator();
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const handleLoadROM = (firmwareFile, basicFile) => {
    const formData = new FormData();
    formData.append('firmware', firmwareFile);
    formData.append('basic', basicFile);

    fetch('http://localhost:8000/api/load_roms/', {
      method: 'POST',
      body: formData,
    })
      .then(res => res.json())
      .then(data => {
        console.log('ROMs chargées:', data);
        alert('ROMs chargées avec succès !');
      })
      .catch(err => {
        console.error('Erreur chargement ROMs:', err);
        alert('Erreur lors du chargement des ROMs.');
      });
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <h1>🖥️ CPC 464 Emulator</h1>
          <div className="led-container">
            <span className={`led ${powerLed ? 'on' : 'off'}`}></span>
            <span className="led-label">POWER</span>
          </div>
          {isResetting && <span className="reset-badge">⏳ RESET</span>}
        </div>
        <div className="header-actions">
          <button className="btn-reset-hard" onClick={reset} title="Reset machine">
            🔄 Reset
          </button>
          <button className="btn-settings" onClick={() => setIsSettingsOpen(true)}>
            ⚙️
          </button>
          <span className="subtitle">Amstrad • Z80 • 64KB</span>
        </div>
      </header>

      <main className="app-main">
        <Screen
          chars={screen.chars}
          colors={screen.colors}
          cursorX={screen.cursor_x}
          cursorY={screen.cursor_y}
          width={screen.width}
          height={screen.height}
          mode={screen.mode}
          loading={loading}
        />
        <Keyboard onKeyPress={sendKey} />
        <Datacorder onFileLoad={(file) => console.log('Fichier chargé:', file)} />
        <StatusBar
          loading={loading}
          error={error}
          onReset={reset}
          isConnected={isConnected}
          powerLed={powerLed}
        />
      </main>

      <footer className="app-footer">
        <p>Clavier AZERTY • Appuyez sur les touches du clavier physique ou cliquez sur les touches virtuelles</p>
      </footer>

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onLoadROM={handleLoadROM}
      />
    </div>
  );
}

export default App;