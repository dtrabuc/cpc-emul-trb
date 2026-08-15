import React, { useState } from 'react';
import { useEmulator } from './hooks/useEmulator';
import Screen from './components/Screen/Screen';
import Keyboard from './components/Keyboard/Keyboard';
import Datacorder from './components/Datacorder/Datacorder';
import StatusBar from './components/StatusBar/StatusBar';
import SettingsModal from './components/Settings/SettingsModal';
import './App.css';

function App() {
  const { 
    screen, 
    loading, 
    error, 
    powerLed, 
    isResetting, 
    romsLoaded,
    tapeStatus,
    sendKey, 
    reset, 
    loadRoms,
    loadTape,
    tapeControl,
    isConnected 
  } = useEmulator();
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const handleLoadROM = (firmwareFile, basicFile) => {
    // Lecture des fichiers et envoi via WebSocket
    const readFileAsHex = (file) => {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          const buffer = e.target.result;
          const bytes = new Uint8Array(buffer);
          let hex = '';
          for (let i = 0; i < bytes.length; i++) {
            hex += bytes[i].toString(16).padStart(2, '0');
          }
          resolve(hex);
        };
        reader.onerror = reject;
        reader.readAsArrayBuffer(file);
      });
    };

    Promise.all([readFileAsHex(firmwareFile), readFileAsHex(basicFile)])
      .then(([firmwareHex, basicHex]) => {
        loadRoms('roms/cpc464_fr.rom', 'roms/basic_1.0.rom');
        console.log('ROMs prêtes à être chargées');
      })
      .catch(err => {
        console.error('Erreur lecture ROMs:', err);
        alert('Erreur lors de la lecture des fichiers ROM.');
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
          loading={loading || !romsLoaded}
        />
        <Keyboard onKeyPress={sendKey} />
        <Datacorder 
          onFileLoad={(file) => {
            console.log('Fichier K7 chargé:', file);
            const reader = new FileReader();
            reader.onload = (e) => {
              const buffer = e.target.result;
              const bytes = new Uint8Array(buffer);
              let hex = '';
              for (let i = 0; i < bytes.length; i++) {
                hex += bytes[i].toString(16).padStart(2, '0');
              }
              loadTape(file.name, hex);
            };
            reader.readAsArrayBuffer(file);
          }}
          tapeStatus={tapeStatus}
          onPlay={() => tapeControl('play')}
          onStop={() => tapeControl('stop')}
          onRewind={() => tapeControl('rewind')}
          onEject={() => tapeControl('eject')}
        />
        <StatusBar
          loading={loading || !romsLoaded}
          error={error}
          onReset={reset}
          isConnected={isConnected}
          powerLed={powerLed}
          romsLoaded={romsLoaded}
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