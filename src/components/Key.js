export class Key {
    constructor(config, onPress, onRelease) {
        this.label = config.label;
        this.code = config.code;
        this.type = config.type || "normal";
        this.size = config.size || null;

        this.onPress = onPress;
        this.onRelease = onRelease;

        this.state = {
            isPressed: false
        };

        this.element = this.createElement();
    }

    createElement() {
        const button = document.createElement("button");
        button.classList.add("key");
        button.dataset.key = this.label;

        if (this.type !== "normal") {
            button.classList.add(`key-${this.type}`);
        }

        if (this.size) {
            button.classList.add(`key-${this.size}`);
        }

        button.textContent = this.label;

        button.addEventListener("mousedown", () => this.press());
        button.addEventListener("mouseup", () => this.release());
        button.addEventListener("mouseleave", () => this.release());
        button.addEventListener("mouseenter", (event) => {
            if (event.buttons & 1) {
                this.press();
            }
        });

        return button;
    }

    press() {
        if (this.state.isPressed) return;
        this.state.isPressed = true;
        this.render();
        if (this.onPress) this.onPress(this);
    }

    release() {
        if (!this.state.isPressed) return;
        this.state.isPressed = false;
        this.render();
        if (this.onRelease) this.onRelease(this);
    }

    render() {
        if (this.state.isPressed) {
            this.element.classList.add("pressed");
        } else {
            this.element.classList.remove("pressed");
        }
    }
}