import React from 'react';
import { useEmulator } from './hooks/useEmulator';
import Screen from './components/Screen/Screen';
import Keyboard from './components/Keyboard/Keyboard';
import Cassette from './components/Cassette/Cassette';
import StatusBar from './components/StatusBar/StatusBar';
import './App.css';

function App() {
  const { screen, loading, error, sendKey, reset } = useEmulator();

  const handleFileLoad = (file) => {
    console.log('Fichier chargé:', file.name);
    // Ici, logique d'envoi au backend plus tard
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
      />
      <Keyboard onKeyPress={sendKey} />
      <Cassette onFileLoad={handleFileLoad} />
      <StatusBar loading={loading} error={error} onReset={reset} />
    </div>
  );
}

export default App;