import React from 'react';
import { useEmulator } from './hooks/useEmulator';
import Screen from './components/Screen/Screen';
import Keyboard from './components/Keyboard/Keyboard';
import Cassette from './components/Cassette/Cassette';
import StatusBar from './components/StatusBar/StatusBar';
import './App.css';

function App() {
  const { screen, status, error, sendKey, reset, isConnected } = useEmulator();

  const handleFileLoad = (file) => {
    console.log('Fichier chargé:', file.name);
  };

  return (
    <div id="cpc-container">
      <Screen
        chars={screen.chars}
        colors={screen.colors}
        cursorX={screen.cursor_x}
        cursorY={screen.cursor_y}
        width={screen.width}
        height={screen.height}
        mode={screen.mode}
        loading={status === 'connecting' || status === 'idle'}
      />
      <Keyboard onKeyPress={sendKey} />
      <Cassette onFileLoad={handleFileLoad} />
      <StatusBar
        loading={status === 'connecting'}
        error={error || (status === 'error' ? 'Connexion perdue' : null)}
        onReset={reset}
        isConnected={isConnected}
      />
    </div>
  );
}

export default App;