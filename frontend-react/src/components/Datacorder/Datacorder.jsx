import React, { useRef, useState } from 'react';
import './Datacorder.css';

function Datacorder({ onFileLoad }) {
  const fileInputRef = useRef(null);
  const [status, setStatus] = useState('Prêt');
  const [isPlaying, setIsPlaying] = useState(false);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file && onFileLoad) {
      onFileLoad(file);
      setStatus(`Chargé : ${file.name}`);
    }
  };

  const handleLoadClick = () => {
    fileInputRef.current.click();
  };

  const handlePlay = () => {
    setIsPlaying(!isPlaying);
    setStatus(isPlaying ? 'Pause' : 'Lecture');
  };

  const handleStop = () => {
    setIsPlaying(false);
    setStatus('Arrêt');
  };

  const handleRewind = () => {
    setStatus('Retour rapide');
    setTimeout(() => setStatus('Prêt'), 1000);
  };

  const handleEject = () => {
    setIsPlaying(false);
    setStatus('Éjecté');
    setTimeout(() => setStatus('Prêt'), 1000);
  };

  return (
    <div className="datacorder-wrapper">
      <div className="datacorder">
        <div className="datacorder-top">
          <span className="datacorder-icon">📼</span>
          <span className="datacorder-title">DATACORDER</span>
        </div>

        <div className="datacorder-body">
          <div className="datacorder-window">
            <div className="datacorder-tape">
              <div className="tape-reel left"></div>
              <div className="tape-band"></div>
              <div className="tape-reel right"></div>
            </div>
          </div>

          <div className="datacorder-controls">
            <button className="datacorder-btn rec" title="Enregistrer">●</button>
            <button className="datacorder-btn stop" onClick={handleStop} title="Stop">■</button>
            <button className={`datacorder-btn play ${isPlaying ? 'active' : ''}`} onClick={handlePlay} title="Lecture">▶</button>
            <button className="datacorder-btn pause" onClick={handlePlay} title="Pause">⏸</button>
            <button className="datacorder-btn rewind" onClick={handleRewind} title="Retour rapide">⏪</button>
            <button className="datacorder-btn eject" onClick={handleEject} title="Éjecter">⏏</button>
          </div>
        </div>

        <div className="datacorder-bottom">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".tap,.cdt"
            style={{ display: 'none' }}
          />
          <button className="datacorder-load-btn" onClick={handleLoadClick}>
            📂 Charger un programme
          </button>
          <span className="datacorder-status">{status}</span>
        </div>
      </div>
    </div>
  );
}

export default Datacorder;