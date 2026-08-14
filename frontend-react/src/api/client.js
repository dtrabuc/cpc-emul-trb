import axios from 'axios';

const API_BASE = '/api';

export const api = {
  // Récupérer l'état de l'écran
  getState: async () => {
    const response = await axios.get(`${API_BASE}/state/`);
    return response.data;
  },

  // Envoyer une touche
  sendKey: async (key) => {
    const response = await axios.post(`${API_BASE}/key/`, { key });
    return response.data;
  },

  // Réinitialiser l'émulateur
  reset: async () => {
    const response = await axios.post(`${API_BASE}/reset/`);
    return response.data;
  },

  // Charger une ROM
  loadROM: async (romId) => {
    const response = await axios.post(`${API_BASE}/load_rom/`, { rom_id: romId });
    return response.data;
  },

  // Sauvegarder l'état
  saveState: async (name = 'Autosave') => {
    const response = await axios.post(`${API_BASE}/save_state/`, { name });
    return response.data;
  },

  // Charger un état
  loadState: async (stateId) => {
    const response = await axios.post(`${API_BASE}/load_state/`, { state_id: stateId });
    return response.data;
  },
};