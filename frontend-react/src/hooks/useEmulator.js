// src/hooks/useEmulator.js
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
  const [powerLed, setPowerLed] = useState(true);
  const [isResetting, setIsResetting] = useState(false);
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
      ws.send(JSON.stringify({ type: 'cycles', count: 16000 }));
      // Demander le statut
      ws.send(JSON.stringify({ type: 'get_status' }));
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
          ws.send(JSON.stringify({ type: 'cycles', count: 16000 }));
        } else if (data.type === 'status') {
          setPowerLed(data.data.power_led);
          setIsResetting(data.data.cpu_reset);
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

  const sendKey = useCallback((key) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'key', key }));
    } else {
      console.warn('[WS] Non connecté, touche ignorée:', key);
    }
  }, []);

  const reset = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'reset' }));
      // Demander le statut après le reset
      setTimeout(() => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({ type: 'get_status' }));
        }
      }, 100);
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [connect]);

  return {
    screen,
    status,
    error,
    powerLed,
    isResetting,
    sendKey,
    reset,
    isConnected: status === 'connected',
  };
}