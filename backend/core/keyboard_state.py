# core/keyboard_state.py

class KeyboardState:
    def __init__(self):
        # 10 lignes de 8 bits (0xFF = aucune touche enfoncée, 0x00 = bit à 0 pour touche appuyée)
        self.rows = [0xFF] * 10

    # Matrice exacte Amstrad CPC 464 (Ligne, Bit)
    KEY_MAP = {
        # Ligne 0
        'f7': (0, 7), 'f8': (0, 6), 'f9': (0, 5), 'f4': (0, 4), '4': (0, 3), '3': (0, 2), '2': (0, 1), '1': (0, 0),
        # Ligne 1
        'f5': (1, 7), 'f6': (1, 6), 'Enter': (1, 5), 'f1': (1, 4), 'f2': (1, 3), 'f0': (1, 2), 'Clr': (1, 1), 'Backspace': (1, 0),
        # Ligne 2
        'f3': (2, 7), 'Control': (2, 5), '\\': (2, 4), '`': (2, 3), 'p': (2, 2), '@': (2, 1), ':': (2, 0), ';': (2, 0),
        # Ligne 3
        '-': (3, 7), '*': (3, 6), 'Return': (3, 5), '+': (3, 4), 'l': (3, 3), 'k': (3, 2), 'j': (3, 1), 'h': (3, 0),
        # Ligne 4
        'o': (4, 7), 'i': (4, 6), 'u': (4, 5), 'y': (4, 4), 'g': (4, 3), 'f': (4, 2), 'd': (4, 1), 's': (4, 0),
        # Ligne 5
        '0': (5, 7), '9': (5, 6), '8': (5, 5), '7': (5, 4), 't': (5, 3), 'r': (5, 2), 'e': (5, 1), 'w': (5, 0),
        # Ligne 6
        '6': (6, 7), '5': (6, 6), 'm': (6, 5), 'b': (6, 3), 'v': (6, 2), 'c': (6, 1), 'x': (6, 0),
        # Ligne 7
        'z': (7, 7), 'CapsLock': (7, 6), 'a': (7, 5), 'Tab': (7, 4), ' ': (7, 3), 'Shift': (7, 1), 'Escape': (7, 0),
        # Ligne 8 (Pave directionnel & Pave numerique)
        'ArrowRight': (8, 7), 'ArrowLeft': (8, 6), 'ArrowUp': (8, 5), 'ArrowDown': (8, 4),
        'NumPadPeriod': (8, 3), 'NumPadEnter': (8, 2), 'NumPadMinus': (8, 1), 'NumPadPlus': (8, 0)
    }

    def key_down(self, key_id):
        if key_id in self.KEY_MAP:
            row, bit = self.KEY_MAP[key_id]
            self.rows[row] &= ~(1 << bit)

    def key_up(self, key_id):
        if key_id in self.KEY_MAP:
            row, bit = self.KEY_MAP[key_id]
            self.rows[row] |= (1 << bit)

    def get_row(self, row_idx):
        if 0 <= row_idx < 10:
            return self.rows[row_idx]
        return 0xFF