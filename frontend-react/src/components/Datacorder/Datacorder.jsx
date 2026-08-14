import React, { useRef } from 'react';
import './Datacorder.css';

function Datacorder({ onFileLoad }) {
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
            <button className="datacorder-btn stop" title="Stop">■</button>
            <button className="datacorder-btn play" title="Lecture">▶</button>
            <button className="datacorder-btn pause" title="Pause">⏸</button>
            <button className="datacorder-btn eject" title="Éjecter">⏏</button>
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
          <span className="datacorder-status">Prêt</span>
        </div>
      </div>
    </div>
  );
}

export default Datacorder;