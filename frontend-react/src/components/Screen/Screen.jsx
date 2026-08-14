import React from 'react';
import './Screen.css';

function Screen({ chars, colors, cursorX, cursorY, width, height, mode }) {
  // Si la grille est 80x40
  const gridCols = width || 80;
  const gridRows = height || 40;
  const cells = [];

  for (let row = 0; row < gridRows; row++) {
    for (let col = 0; col < gridCols; col++) {
      const char = (chars[row] && chars[row][col]) || ' ';
      const color = (colors[row] && colors[row][col]) || '#ffff00';
      const isCursor = row === cursorY && col === cursorX;

      cells.push(
        <div
          key={`${row}-${col}`}
          className={`cell ${isCursor ? 'cursor' : ''}`}
          style={{ color }}
        >
          {char}
        </div>
      );
    }
  }

  return (
    <div id="monitor">
      <div id="screen">{cells}</div>
      <div id="screen-overlay"></div>
    </div>
  );
}

export default Screen;