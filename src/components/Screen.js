export class Screen {
    constructor(containerId, options = { cols: 80, rows: 40 }) {
        this.container = document.getElementById(containerId);

        if (!this.container) {
            console.error(`Screen: L'élément avec l'ID "${containerId}" est introuvable.`);
            return;
        }

        this.cols = options.cols;
        this.rows = options.rows;

        // Texte initial exact demandé
        this.state = {
            text: "Amstrad Locomotive LTD (c) 1984 BASIC 1.0 by Microsoft Corp."
        };

        this.cells = [];
        this.cursorVisible = true;

        this.initDOM();
        this.startCursorBlink();
    }

    initDOM() {
        this.container.innerHTML = "";
        this.cells = [];
        const totalCells = this.cols * this.rows;

        // Génération de la grille de 80x40 sous forme de tableau d'éléments .cell
        for (let i = 0; i < totalCells; i++) {
            const cell = document.createElement("span");
            cell.classList.add("cell");
            this.container.appendChild(cell);
            this.cells.push(cell);
        }

        this.render();
    }

    // Gestion du clignotement à 500ms
    startCursorBlink() {
        setInterval(() => {
            this.cursorVisible = !this.cursorVisible;
            this.render();
        }, 500);
    }

    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.render();
    }

    setText(newText) {
        this.setState({ text: newText });
    }

    render() {
        const text = this.state.text;
        const totalCells = this.cells.length;

        for (let i = 0; i < totalCells; i++) {
            if (i < text.length) {
                // Caractères du texte
                this.cells[i].textContent = text[i];
                this.cells[i].classList.remove("cursor");
            } else if (i === text.length && this.cursorVisible) {
                // Rectangle de saisie █ clignotant juste à la suite
                this.cells[i].textContent = "█";
                this.cells[i].classList.add("cursor");
            } else {
                // Cellules vides du tableau
                this.cells[i].textContent = " ";
                this.cells[i].classList.remove("cursor");
            }
        }
    }
}