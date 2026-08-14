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
  const [status, setStatus] = useState('idle'); // idle | connecting | connected | error
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeout = useRef(null);

  const connect = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      return;
    }

    setStatus('connecting');
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('[WS] Connecté au backend');
      setStatus('connected');
      setError(null);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'screen') {
          const screenData = data.data;
          setScreen({
            chars: screenData.chars || [],
            colors: screenData.colors || [],
            cursor_x: screenData.cursor_x || 0,
            cursor_y: screenData.cursor_y || 0,
            width: screenData.width || 80,
            height: screenData.height || 40,
            mode: screenData.mode || 1,
          });
        }
      } catch (e) {
        console.error('[WS] Erreur de parsing:', e);
      }
    };

    ws.onclose = () => {
      console.log('[WS] Déconnecté');
      setStatus('error');
      // Reconnexion automatique après 2s
      reconnectTimeout.current = setTimeout(() => {
        connect();
      }, 2000);
    };

    ws.onerror = (err) => {
      console.error('[WS] Erreur:', err);
      setError('Erreur de connexion WebSocket');
    };
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
      reconnectTimeout.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setStatus('idle');
  }, []);

  const sendKey = useCallback((key) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'key',
        key: key,
      }));
    } else {
      console.warn('[WS] Non connecté, impossible d\'envoyer la touche:', key);
    }
  }, []);

  const reset = useCallback(() => {
    // On envoie une commande de reset via WebSocket
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'reset',
      }));
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    screen,
    status,
    error,
    sendKey,
    reset,
    isConnected: status === 'connected',
  };
}