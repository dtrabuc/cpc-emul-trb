import React from 'react';
import './Screen.css';

const STARTUP_TEXT = [
  'Amstrad 64K Microcomputer <v1>',
  '(c) 1984 Amstrad Electronics',
  'this emulator created by Dydy 2026',
  'And Locomotive Software LTD',
  '',
  'BASIC 1.0',
  '',
  'Ready',
];

function Screen({ chars, colors, cursorX, cursorY, width, height, mode, loading }) {
  const gridChars = [];
  const gridColors = [];
  const useStartup = loading || !chars || chars.length === 0;

  for (let row = 0; row < height; row++) {
    gridChars[row] = [];
    gridColors[row] = [];
    for (let col = 0; col < width; col++) {
      if (useStartup && row < STARTUP_TEXT.length && col < STARTUP_TEXT[row].length) {
        gridChars[row][col] = STARTUP_TEXT[row][col] || ' ';
        gridColors[row][col] = '#ffff00';
      } else if (useStartup) {
        gridChars[row][col] = ' ';
        gridColors[row][col] = '#ffff00';
      } else {
        gridChars[row][col] = (chars[row] && chars[row][col]) || ' ';
        gridColors[row][col] = (colors[row] && colors[row][col]) || '#ffff00';
      }
    }
  }

  const defaultCursorX = STARTUP_TEXT[7]?.length || 5;
  const defaultCursorY = 7;
  const finalCursorX = (useStartup || cursorX === undefined) ? defaultCursorX : cursorX;
  const finalCursorY = (useStartup || cursorY === undefined) ? defaultCursorY : cursorY;

  const cells = [];
  for (let row = 0; row < height; row++) {
    for (let col = 0; col < width; col++) {
      const char = gridChars[row]?.[col] || ' ';
      const color = gridColors[row]?.[col] || '#ffff00';
      const isCursor = row === finalCursorY && col === finalCursorX;
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