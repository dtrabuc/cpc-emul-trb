import React, { useEffect } from 'react';
import './Keyboard.css';

// Format des touches : { label: 'texte', span: largeur, color: 'couleur' }
// Pour les touches multi-lignes, utiliser \n pour le retour à la ligne
const KEY_ROWS = [
  // LIGNE 1
  [
    { label: 'Esc', span: 1, color: 'red' },
    { label: '1\n&', span: 1 },
    { label: '2\né', span: 1 },
    { label: '3\n"', span: 1 },
    { label: "4\n'", span: 1 },
    { label: '5\n(', span: 1 },
    { label: '6\n]', span: 1 },
    { label: '7\nè', span: 1 },
    { label: '8\n!', span: 1 },
    { label: '9\nç', span: 1 },
    { label: '0\nà', span: 1 },
    { label: '[\n)', span: 1 },
    { label: '_\n-', span: 2 },
    { label: 'CLR', span: 1, color: 'red' },
    { label: 'DEL', span: 1, color: 'red' },
  ],
  // LIGNE 2
  [
    { label: 'TAB', span: 1, color: 'gray' },
    { label: 'A', span: 1 },
    { label: 'Z', span: 1 },
    { label: 'E', span: 1 },
    { label: 'R', span: 1 },
    { label: 'T', span: 1 },
    { label: 'Y', span: 1 },
    { label: 'U', span: 1 },
    { label: 'I', span: 1 },
    { label: 'O', span: 1 },
    { label: 'P', span: 1 },
    { label: '/\n^', span: 1 },
    { label: '<\n*', span: 2 },
    { label: 'ENTER', span: 2, color: 'green' },
  ],
  // LIGNE 3
  [
    { label: 'CAPS\nLOCK', span: 2, color: 'gray' },
    { label: 'Q', span: 1 },
    { label: 'S', span: 1 },
    { label: 'D', span: 1 },
    { label: 'F', span: 1 },
    { label: 'G', span: 1 },
    { label: 'H', span: 1 },
    { label: 'J', span: 1 },
    { label: 'K', span: 1 },
    { label: 'L', span: 1 },
    { label: 'M', span: 1 },
    { label: '%\nù', span: 1 },
    { label: '>\n#', span: 2 },
  ],
  // LIGNE 4
  [
    { label: 'SHIFT', span: 2, color: 'gray' },
    { label: 'W', span: 1 },
    { label: 'X', span: 1 },
    { label: 'C', span: 1 },
    { label: 'V', span: 1 },
    { label: 'B', span: 1 },
    { label: 'N', span: 1 },
    { label: '?\n,', span: 2 },
    { label: '.\n;', span: 2 },
    { label: '/\n:', span: 2 },
    { label: '"\n+', span: 2 },
    { label: '@\n$', span: 2 },
    { label: 'SHIFT', span: 2, color: 'gray' },
  ],
  // LIGNE 5
  [
    { label: 'SPACE', span: 18, color: 'gray' },
    { label: 'CTRL', span: 1, color: 'gray' },
  ],
];

const NUMPAD_KEYS = [
  ['7', '8', '9'],
  ['4', '5', '6'],
  ['1', '2', '3'],
  ['0', '.', 'ENTER'],
];

const getColorClass = (color) => {
  switch (color) {
    case 'red': return 'key-red';
    case 'green': return 'key-green';
    case 'gray': return 'key-gray';
    default: return '';
  }
};

function Keyboard({ onKeyPress }) {
  const handleKeyClick = (label) => {
    // Si la touche a un saut de ligne, on prend juste le premier caractère
    const cleanLabel = label.split('\n')[0];
    if (onKeyPress) onKeyPress(cleanLabel);
  };

  useEffect(() => {
    const handlePhysicalKey = (e) => {
      const key = e.key;
      const preventKeys = [' ', 'Tab', 'Enter', 'Escape', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'];
      if (preventKeys.includes(key)) e.preventDefault();

      let mapped = key;
      if (key === 'Enter') mapped = 'ENTER';
      if (key === 'Backspace') mapped = 'DEL';
      if (key === 'Escape') mapped = 'Esc';
      if (key === 'Tab') mapped = 'TAB';
      if (key === ' ') mapped = 'SPACE';
      if (key === 'Control') mapped = 'CTRL';
      if (key === 'Shift') mapped = 'SHIFT';
      if (key.startsWith('Arrow')) mapped = key;

      if (onKeyPress) onKeyPress(mapped);
    };

    window.addEventListener('keydown', handlePhysicalKey);
    return () => window.removeEventListener('keydown', handlePhysicalKey);
  }, [onKeyPress]);

  return (
    <div className="keyboard-wrapper">
      <div className="keyboard-main">
        <div id="virtual-keyboard">
          {KEY_ROWS.map((row, rowIndex) => (
            <div key={rowIndex} className="kbd-row">
              {row.map((key, keyIndex) => (
                <button
                  key={keyIndex}
                  className={`key ${getColorClass(key.color)} ${key.span > 1 ? 'key-wide' : ''}`}
                  style={{ flex: key.span }}
                  onClick={() => handleKeyClick(key.label)}
                >
                  {key.label.split('\n').map((line, i) => (
                    <span key={i} className="key-line">{line}</span>
                  ))}
                </button>
              ))}
            </div>
          ))}
        </div>

        <div className="keyboard-side">
          <div className="arrows">
            <button className="key key-gray arrow-up" onClick={() => handleKeyClick('ArrowUp')}>↑</button>
            <button className="key key-gray arrow-left" onClick={() => handleKeyClick('ArrowLeft')}>←</button>
            <button className="key key-gray arrow-down" onClick={() => handleKeyClick('ArrowDown')}>↓</button>
            <button className="key key-gray arrow-right" onClick={() => handleKeyClick('ArrowRight')}>→</button>
          </div>

          <div className="numpad">
            {NUMPAD_KEYS.map((row, rowIndex) => (
              <div key={rowIndex} className="numpad-row">
                {row.map((key) => (
                  <button
                    key={key}
                    className={`key ${key === 'ENTER' ? 'key-green' : 'key-gray'}`}
                    onClick={() => handleKeyClick(key)}
                  >
                    {key}
                  </button>
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Keyboard;