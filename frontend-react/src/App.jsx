import React from 'react';
import { useEmulator } from './hooks/useEmulator';
import Screen from './components/Screen/Screen';
import Keyboard from './components/Keyboard/Keyboard';
import Datacorder from './components/Datacorder/Datacorder';
import StatusBar from './components/StatusBar/StatusBar';
import './App.css';

function App() {
  const { screen, loading, error, sendKey, reset, isConnected } = useEmulator();

  const handleFileLoad = (file) => {
    console.log('Fichier chargé:', file.name);
    // Ici, logique d'envoi au backend plus tard
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🖥️ CPC 464 Emulator</h1>
        <span className="subtitle">Amstrad • Z80 • 64KB</span>
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
        <Datacorder onFileLoad={handleFileLoad} />
        <StatusBar
          loading={loading}
          error={error}
          onReset={reset}
          isConnected={isConnected}
        />
      </main>

      <footer className="app-footer">
        <p>Clavier AZERTY • Appuyez sur les touches du clavier physique ou cliquez sur les touches virtuelles</p>
      </footer>
    </div>
  );
}

export default App;