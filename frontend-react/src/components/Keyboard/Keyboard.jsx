import React, { useEffect } from 'react';
import './Keyboard.css';

// LAYOUT EXACT DU FICHIER EXCEL
const KEY_ROWS = [
  ['Esc', '1&', '2é', '3"', "4'", '5(', '6]', '7è', '8!', '9ç', '0à', '[)', '=-_', 'CLR', 'DEL'],
  ['TAB', 'A', 'Z', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '/^', '<*', 'ENTER'],
  ['CAPS LOCK', 'Q', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', '%ù', '>#'],
  ['SHIFT', 'W', 'X', 'C', 'V', 'B', 'N', '?,', '.;', '/:', '="+', '@$', 'SHIFT'],
  ['SPACE', 'CTRL'],
];

const NUMPAD_KEYS = [
  ['7', '8', '9'],
  ['4', '5', '6'],
  ['1', '2', '3'],
  ['0', '.', 'ENTER'],
];

// COULEURS AUTHENTIQUES
const KEY_COLORS = {
  'Esc': 'key-red',
  'CLR': 'key-red',
  'DEL': 'key-red',
  'ENTER': 'key-green',
  'TAB': 'key-gray',
  'CAPS LOCK': 'key-gray',
  'SHIFT': 'key-gray',
  'CTRL': 'key-gray',
  'SPACE': 'key-gray',
};

// LIBELLÉS SPÉCIAUX
const SPECIAL_LABELS = {
  'Esc': 'Esc',
  'TAB': 'Tab',
  'CAPS LOCK': 'Caps',
  'SHIFT': '⇧',
  'CTRL': 'Ctrl',
  'SPACE': '␣',
  'ENTER': '↵',
  'CLR': 'CLR',
  'DEL': '⌫',
};

const WIDE_KEYS = ['Esc', 'TAB', 'CAPS LOCK', 'SHIFT', 'CTRL', 'ENTER', 'CLR', 'DEL'];

function Keyboard({ onKeyPress }) {
  const handleClick = (label) => {
    if (onKeyPress) {
      console.log('[FRONT] Touche cliquée:', label);
      onKeyPress(label);
    }
  };

  useEffect(() => {
    const handlePhysical = (e) => {
      const key = e.key;
      if ([' ', 'Tab', 'Enter', 'Escape', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(key)) {
        e.preventDefault();
      }
      let mapped = key;
      if (key === 'Enter') mapped = 'ENTER';
      if (key === 'Backspace') mapped = 'DEL';
      if (key === 'Escape') mapped = 'Esc';
      if (key === 'Tab') mapped = 'TAB';
      if (key === ' ') mapped = 'SPACE';
      if (key === 'Control') mapped = 'CTRL';
      if (key === 'Shift') mapped = 'SHIFT';
      console.log('[FRONT] Touche physique:', key, '→', mapped);
      if (onKeyPress) onKeyPress(mapped);
    };
    window.addEventListener('keydown', handlePhysical);
    return () => window.removeEventListener('keydown', handlePhysical);
  }, [onKeyPress]);

  return (
    <div className="keyboard-wrapper">
      <div className="keyboard-main">
        <div id="virtual-keyboard">
          {KEY_ROWS.map((row, rowIndex) => (
            <div key={rowIndex} className="kbd-row">
              {row.map((label, idx) => {
                let className = 'key';
                if (KEY_COLORS[label]) className += ` ${KEY_COLORS[label]}`;
                if (label === 'SPACE') className += ' key-space';
                if (WIDE_KEYS.includes(label)) className += ' key-wide';
                const display = SPECIAL_LABELS[label] || label;
                return (
                  <button key={idx} className={className} onClick={() => handleClick(label)}>
                    {display}
                  </button>
                );
              })}
            </div>
          ))}
        </div>

        <div className="keyboard-side">
          <div className="arrows">
            <button className="key key-gray arrow-up" onClick={() => handleClick('ArrowUp')}>↑</button>
            <button className="key key-gray arrow-left" onClick={() => handleClick('ArrowLeft')}>←</button>
            <button className="key key-gray arrow-down" onClick={() => handleClick('ArrowDown')}>↓</button>
            <button className="key key-gray arrow-right" onClick={() => handleClick('ArrowRight')}>→</button>
          </div>
          <div className="numpad">
            {NUMPAD_KEYS.map((row, rowIndex) => (
              <div key={rowIndex} className="numpad-row">
                {row.map((key) => (
                  <button
                    key={key}
                    className={`key ${key === 'ENTER' ? 'key-green' : 'key-gray'}`}
                    onClick={() => handleClick(key)}
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