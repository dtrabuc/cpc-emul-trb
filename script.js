document.addEventListener("DOMContentLoaded", () => {
  const COLS = 80;
  const ROWS = 40;
  const TOTAL_CELLS = COLS * ROWS;

  const screen = document.getElementById("screen");
  if (!screen) return;

  screen.innerHTML = "";

  const fragment = document.createDocumentFragment();
  for (let i = 0; i < TOTAL_CELLS; i++) {
    const cell = document.createElement("span");
    cell.className = "cell";
    fragment.appendChild(cell);
  }
  screen.appendChild(fragment);

  let cursorX = 0;
  let cursorY = 0;

  function getCell(x, y) {
    if (x < 0 || x >= COLS || y < 0 || y >= ROWS) return null;
    return screen.children[y * COLS + x];
  }

  function updateCursor() {
    const oldCursor = screen.querySelector(".cell.cursor");
    if (oldCursor) oldCursor.classList.remove("cursor");

    const newCell = getCell(cursorX, cursorY);
    if (newCell) newCell.classList.add("cursor");
  }

  window.printAt = function(x, y, text) {
    let currentX = x;
    let currentY = y;

    for (let i = 0; i < text.length; i++) {
      if (currentX >= COLS) {
        currentX = 0;
        currentY++;
      }
      if (currentY >= ROWS) break;

      const cell = getCell(currentX, currentY);
      if (cell) cell.textContent = text[i];
      currentX++;
    }
  };

  window.handleInput = function(key) {
    if (key === "Enter") {
      cursorX = 0;
      if (cursorY < ROWS - 1) cursorY++;
    } else if (key === "Backspace") {
      if (cursorX > 0) {
        cursorX--;
        const cell = getCell(cursorX, cursorY);
        if (cell) cell.textContent = "";
      }
    } else if (key === "Escape") {
      for (let i = 0; i < TOTAL_CELLS; i++) {
        screen.children[i].textContent = "";
      }
      cursorX = 0;
      cursorY = 0;
    } else if (key.length === 1) {
      const cell = getCell(cursorX, cursorY);
      if (cell) {
        // En BASIC CPC, les lettres apparaissent par défaut en majuscules
        cell.textContent = key.toUpperCase();
        cursorX++;
        if (cursorX >= COLS) {
          cursorX = 0;
          if (cursorY < ROWS - 1) cursorY++;
        }
      }
    }
    updateCursor();
  };

  window.addEventListener("keydown", (e) => {
    if (e.key === "Tab" || e.key === "Process") e.preventDefault();
    window.handleInput(e.key);
  });

  // Message d'accueil du Firmware CPC
  window.printAt(0, 0, "Amstrad 64K Microcomputer  v1 (AZERTY)");
  window.printAt(0, 1, "BASIC 1.1");
  window.printAt(0, 3, "Ready");
  
  cursorX = 0;
  cursorY = 4;
  updateCursor();
});