const API_BASE = 'http://localhost:8000/api';

async function fetchScreen() {
    try {
        const response = await fetch(`${API_BASE}/state/`);
        const data = await response.json();
        renderScreen(data);
    } catch (error) {
        console.error('Erreur de connexion au backend:', error);
    }
}

function renderScreen(data) {
    const cells = document.querySelectorAll('.cell');
    const chars = data.chars || [];
    const colors = data.colors || [];
    const width = data.width || 80;
    const cursorX = data.cursor_x || 0;
    const cursorY = data.cursor_y || 0;

    cells.forEach((cell, index) => {
        const row = Math.floor(index / width);
        const col = index % width;
        const char = (chars[row] && chars[row][col]) ? chars[row][col] : ' ';
        const color = (colors[row] && colors[row][col]) ? colors[row][col] : '#FFFFFF';
        
        cell.textContent = char;
        cell.style.color = color;
        cell.classList.toggle('cursor', row === cursorY && col === cursorX);
    });
}

async function sendKey(key) {
    try {
        await fetch(`${API_BASE}/key/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key: key })
        });
        await fetchScreen();
    } catch (error) {
        console.error('Erreur:', error);
    }
}

// Remplacer window.handleInput
window.handleInput = sendKey;

setInterval(fetchScreen, 50);
fetchScreen();