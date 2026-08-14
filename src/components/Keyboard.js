import { Key } from "./Key.js";

export class Keyboard {
    constructor(containerId, layout, onKeyPress) {
        this.container = document.getElementById(containerId);
        this.layout = layout;
        this.onKeyPress = onKeyPress;

        this.keysMap = new Map();

        this.initDOM();
        this.bindPhysicalKeyboard();
    }

    createKeyInstance(config) {
        const key = new Key(
            config,
            (k) => this.handleKeyPress(k),
            () => {}
        );

        if (config.code) {
            this.keysMap.set(config.code, key);
        }

        return key;
    }

    initDOM() {
        this.container.innerHTML = "";

        // 1. CLAVIER PRINCIPAL
        const mainKeyboard = document.createElement("div");
        mainKeyboard.classList.add("main-keyboard");

        this.layout.main.forEach(rowData => {
            const row = document.createElement("div");
            row.classList.add("key-row");

            rowData.forEach(keyConfig => {
                const key = this.createKeyInstance(keyConfig);
                row.appendChild(key.element);
            });

            mainKeyboard.appendChild(row);
        });

        // Rangée espace / ctrl
        const bottomRow = document.createElement("div");
        bottomRow.classList.add("bottom-row");

        const spaceKey = this.createKeyInstance({ label: "", code: "Space", type: "normal", size: "space" });
        const ctrlKey = this.createKeyInstance({ label: "CTRL", code: "ControlLeft", type: "ctrl" });

        bottomRow.appendChild(spaceKey.element);
        bottomRow.appendChild(ctrlKey.element);
        mainKeyboard.appendChild(bottomRow);

        this.container.appendChild(mainKeyboard);

        // 2. BLOC CURSEURS
        const cursorBlock = document.createElement("div");
        cursorBlock.classList.add("cursor-block");

        const cursors = [
            { label: "↑", code: "ArrowUp", className: "cursor-up" },
            { label: "←", code: "ArrowLeft", className: "cursor-left" },
            { label: "COPY", code: "AltLeft", type: "green", className: "cursor-copy" },
            { label: "→", code: "ArrowRight", className: "cursor-right" },
            { label: "↓", code: "ArrowDown", className: "cursor-down" }
        ];

        cursors.forEach(config => {
            const key = this.createKeyInstance(config);
            key.element.classList.add(config.className);
            cursorBlock.appendChild(key.element);
        });

        this.container.appendChild(cursorBlock);

        // 3. PAVÉ NUMÉRIQUE
        const numpad = document.createElement("div");
        numpad.classList.add("numpad");

        this.layout.numpad.forEach(config => {
            const key = this.createKeyInstance(config);
            if (config.label === "ENTER") {
                key.element.classList.add("numpad-enter");
            }
            numpad.appendChild(key.element);
        });

        this.container.appendChild(numpad);
    }

    handleKeyPress(keyInstance) {
        if (this.onKeyPress) {
            this.onKeyPress(keyInstance);
        }
    }

    bindPhysicalKeyboard() {
        document.addEventListener("keydown", (event) => {
            if (event.repeat) return;
            const key = this.keysMap.get(event.code);
            if (key) key.press();
        });

        document.addEventListener("keyup", (event) => {
            const key = this.keysMap.get(event.code);
            if (key) key.release();
        });
    }
}