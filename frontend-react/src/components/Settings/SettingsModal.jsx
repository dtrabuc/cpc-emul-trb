import React, { useState } from 'react';
import './SettingsModal.css';

function SettingsModal({ isOpen, onClose, onLoadROM }) {
  const [firmwareFile, setFirmwareFile] = useState(null);
  const [basicFile, setBasicFile] = useState(null);

  const handleLoad = () => {
    if (firmwareFile && basicFile) {
      onLoadROM(firmwareFile, basicFile);
      onClose();
    } else {
      alert('Veuillez sélectionner les deux fichiers ROM.');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="settings-overlay">
      <div className="settings-modal">
        <h2>⚙️ Paramètres CPC 464</h2>
        <div className="settings-group">
          <label>Firmware (cpc464_fr.rom)</label>
          <input type="file" accept=".rom" onChange={(e) => setFirmwareFile(e.target.files[0])} />
        </div>
        <div className="settings-group">
          <label>BASIC 1.0 (basic_1.0.rom)</label>
          <input type="file" accept=".rom" onChange={(e) => setBasicFile(e.target.files[0])} />
        </div>
        <div className="settings-actions">
          <button onClick={handleLoad}>Charger les ROMs</button>
          <button onClick={onClose}>Fermer</button>
        </div>
      </div>
    </div>
  );
}

export default SettingsModal;