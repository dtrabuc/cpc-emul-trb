import React, { useRef } from 'react';
import './Cassette.css';

function Cassette({ onFileLoad }) {
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file && onFileLoad) {
      onFileLoad(file);
    }
  };

  const handleLoadClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="cassette-container">
      <div className="cassette">
        <div className="cassette-top">
          <span className="cassette-icon">📼</span>
          <span className="cassette-title">CASSETTE</span>
        </div>

        <div className="cassette-body">
          <div className="cassette-window">
            <div className="cassette-tape">
              <div className="tape-reel left"></div>
              <div className="tape-reel right"></div>
              <div className="tape-band"></div>
            </div>
          </div>

          <div className="cassette-controls">
            <button className="cassette-btn rec" title="Enregistrer">●</button>
            <button className="cassette-btn stop" title="Stop">■</button>
            <button className="cassette-btn play" title="Lecture">▶</button>
            <button className="cassette-btn pause" title="Pause">⏸</button>
            <button className="cassette-btn eject" title="Éjecter">⏏</button>
          </div>
        </div>

        <div className="cassette-bottom">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".tap,.cdt"
            style={{ display: 'none' }}
          />
          <button className="cassette-load-btn" onClick={handleLoadClick}>
            📂 Charger un programme
          </button>
          <span className="cassette-status">Prêt</span>
        </div>
      </div>
    </div>
  );
}

export default Cassette;