console.log("App.js est bien chargé !");

import { Screen } from "./components/Screen.js";
import { Keyboard } from "./components/Keyboard.js";

const keyboardLayout = {
    main: [
        [
            { label: "ESC", code: "Escape", type: "esc" },
            { label: "1\n&", code: "Digit1" },
            { label: "2\né", code: "Digit2" },
            { label: "3\n\"", code: "Digit3" },
            { label: "4\n'", code: "Digit4" },
            { label: "5\n(", code: "Digit5" },
            { label: "6\n]", code: "Digit6" },
            { label: "7\nè", code: "Digit7" },
            { label: "8\n!", code: "Digit8" },
            { label: "9\nç", code: "Digit9" },
            { label: "0\nà", code: "Digit0" },
            { label: "-\n_", code: "Minus" },
            { label: "=\n+", code: "Equal" },
            { label: "CLR", code: "Backspace" },
            { label: "DEL", code: "Delete", type: "green", size: "wide" }
        ],
        [
            { label: "TAB", code: "Tab", type: "green", size: "wide" },
            { label: "A", code: "KeyQ" },
            { label: "Z", code: "KeyW" },
            { label: "E", code: "KeyE" },
            { label: "R", code: "KeyR" },
            { label: "T", code: "KeyT" },
            { label: "Y", code: "KeyY" },
            { label: "U", code: "KeyU" },
            { label: "I", code: "KeyI" },
            { label: "O", code: "KeyO" },
            { label: "P", code: "KeyP" },
            { label: "^\n¦", code: "BracketLeft" },
            { label: "<\n*", code: "BracketRight" },
            { label: "ENTER", code: "Enter", type: "blue", size: "wide" }
        ],
        [
            { label: "CAPS\nLOCK", code: "CapsLock", type: "green", size: "xwide" },
            { label: "Q", code: "KeyA" },
            { label: "S", code: "KeyS" },
            { label: "D", code: "KeyD" },
            { label: "F", code: "KeyF" },
            { label: "G", code: "KeyG" },
            { label: "H", code: "KeyH" },
            { label: "J", code: "KeyJ" },
            { label: "K", code: "KeyK" },
            { label: "L", code: "KeyL" },
            { label: "M", code: "Semicolon" },
            { label: "%\nù", code: "Quote" },
            { label: ">\n#", code: "Backslash" },
            { label: "", type: "blue", size: "enter-continuation" }
        ],
        [
            { label: "SHIFT", code: "ShiftLeft", type: "green", size: "xwide" },
            { label: "W", code: "KeyZ" },
            { label: "X", code: "KeyX" },
            { label: "C", code: "KeyC" },
            { label: "V", code: "KeyV" },
            { label: "B", code: "KeyB" },
            { label: "N", code: "KeyN" },
            { label: "?\n,", code: "Comma" },
            { label: ";\n.", code: "Period" },
            { label: "/\n:", code: "Slash" },
            { label: "+\n=", code: "Equal" },
            { label: "@\\\n$", code: "Backquote" },
            { label: "SHIFT", code: "ShiftRight", type: "green", size: "xwide" }
        ]
    ],
    numpad: [
        { label: "7", code: "Numpad7" }, { label: "8", code: "Numpad8" }, { label: "9", code: "Numpad9" },
        { label: "4", code: "Numpad4" }, { label: "5", code: "Numpad5" }, { label: "6", code: "Numpad6" },
        { label: "1", code: "Numpad1" }, { label: "2", code: "Numpad2" }, { label: "3", code: "Numpad3" },
        { label: "0", code: "Numpad0" }, { label: ".", code: "NumpadDecimal" }, { label: "ENTER", code: "NumpadEnter", type: "blue" }
    ]
};

window.addEventListener("DOMContentLoaded", () => {
    const screen = new Screen("screen");

    const keyboard = new Keyboard("keyboard", keyboardLayout, (key) => {
        if (key.label && key.label.length === 1) {
            screen.setText(screen.state.text + key.label);
        }
    });
});