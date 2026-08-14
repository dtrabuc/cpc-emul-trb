import { useState, useEffect, useCallback, useRef } from 'react';

const API_BASE = '/api';

export function useEmulator() {
  const [screen, setScreen] = useState({
    chars: [],
    colors: [],
    cursor_x: 5,    // Position par défaut du curseur après "Ready"
    cursor_y: 8,     // Ligne après "Ready"
    width: 80,
    height: 40,
    mode: 1,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);
  const firstFetchDone = useRef(false);

  const fetchScreen = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/state/`);
      if (!response.ok) throw new Error('Erreur réseau');
      const data = await response.json();

      // Si le backend renvoie des données, on les utilise
      if (data.chars && data.chars.length > 0) {
        setScreen({
          chars: data.chars || [],
          colors: data.colors || [],
          cursor_x: data.cursor_x || 0,
          cursor_y: data.cursor_y || 0,
          width: data.width || 80,
          height: data.height || 40,
          mode: data.mode || 1,
        });
        setError(null);
      }
      // Sinon, on garde l'écran de démarrage
      setLoading(false);
      firstFetchDone.current = true;
    } catch (err) {
      setError('Erreur de connexion au backend');
      console.error(err);
      setLoading(false);
    }
  }, []);

  const sendKey = useCallback(async (key) => {
    try {
      await fetch(`${API_BASE}/key/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key }),
      });
      // Après l'envoi d'une touche, on rafraîchit l'écran
      await fetchScreen();
    } catch (err) {
      console.error('Erreur clavier:', err);
    }
  }, [fetchScreen]);

  const reset = useCallback(async () => {
    try {
      await fetch(`${API_BASE}/reset/`, { method: 'POST' });
      await fetchScreen();
    } catch (err) {
      console.error('Erreur reset:', err);
    }
  }, [fetchScreen]);

  useEffect(() => {
    fetchScreen();
    intervalRef.current = setInterval(fetchScreen, 50);
    return () => clearInterval(intervalRef.current);
  }, [fetchScreen]);

  return {
    screen,
    loading,
    error,
    sendKey,
    reset,
  };
}