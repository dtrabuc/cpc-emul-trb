import { useState, useEffect, useCallback, useRef } from 'react';
import { api } from '../api/client';
import { getScancode } from '../utils/keyMapping';

export function useEmulator() {
  const [screen, setScreen] = useState({
    chars: [],
    colors: [],
    cursor_x: 0,
    cursor_y: 0,
    width: 80,
    height: 40,
    mode: 1,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  const fetchScreen = useCallback(async () => {
    try {
      const data = await api.getState();
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
    } catch (err) {
      setError('Erreur de connexion au backend');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const sendKey = useCallback(async (key) => {
    try {
      // Récupérer le scancode
      const scancode = getScancode(key);
      
      // Si scancode = 0, on envoie quand même la touche brute
      // pour permettre au backend de gérer le mapping
      await api.sendKey(key);
      // Rafraîchir l'écran après la touche
      await fetchScreen();
    } catch (err) {
      console.error('Erreur lors de l\'envoi de la touche:', err);
    }
  }, [fetchScreen]);

  const reset = useCallback(async () => {
    try {
      await api.reset();
      await fetchScreen();
    } catch (err) {
      console.error('Erreur lors de la réinitialisation:', err);
    }
  }, [fetchScreen]);

  useEffect(() => {
    fetchScreen();

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    intervalRef.current = setInterval(fetchScreen, 50);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [fetchScreen]);

  return {
    screen,
    loading,
    error,
    sendKey,
    reset,
    fetchScreen,
  };
}