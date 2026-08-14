import { useState, useEffect, useCallback, useRef } from 'react';

const WS_URL = 'ws://localhost:8000/ws/emulator/';

export function useEmulator() {
  const [screen, setScreen] = useState({
    chars: [],
    colors: [],
    cursor_x: 5,
    cursor_y: 8,
    width: 80,
    height: 40,
    mode: 1,
  });
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeout = useRef(null);

  const connect = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return;

    setStatus('connecting');
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('[WS] Connecté');
      setStatus('connected');
      setError(null);
      // Démarrer le cycle d'exécution
      sendCycles(16000);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'screen') {
          const d = data.data;
          setScreen({
            chars: d.chars || [],
            colors: d.colors || [],
            cursor_x: d.cursor_x || 0,
            cursor_y: d.cursor_y || 0,
            width: d.width || 80,
            height: d.height || 40,
            mode: d.mode || 1,
          });
          // Demander le prochain lot de cycles
          sendCycles(16000);
        }
      } catch (e) {
        console.error('[WS] Erreur parsing:', e);
      }
    };

    ws.onclose = () => {
      console.log('[WS] Déconnecté');
      setStatus('error');
      reconnectTimeout.current = setTimeout(connect, 2000);
    };

    ws.onerror = (err) => {
      console.error('[WS] Erreur:', err);
      setError('Erreur de connexion');
    };
  }, []);

  const sendCycles = useCallback((count) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'cycles',
        count: count,
      }));
    }
  }, []);

  const sendKey = useCallback((key) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'key',
        key: key,
      }));
    } else {
      console.warn('[WS] Non connecté, touche ignorée:', key);
    }
  }, []);

  const reset = useCallback(() => {
    // Le reset se fait via la reconnexion
    if (wsRef.current) {
      wsRef.current.close();
    }
    setTimeout(connect, 100);
  }, [connect]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return {
    screen,
    status,
    error,
    sendKey,
    reset,
    isConnected: status === 'connected',
  };
}