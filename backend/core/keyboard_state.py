# Dans core/keyboard_state.py
class CPCKey:
    def __init__(self, line: int, bit_pos: int):
        self.line = line
        self.bit_pos = bit_pos

class KeyboardState:
    A = CPCKey(8, 5)
    B = CPCKey(6, 6)
    # ... etc.

    # Matrice de 10 lignes x 10 colonnes
    _matrix = [0xFF] * 10

    @classmethod
    def press_key(cls, key: CPCKey):
        cls._matrix[key.line] &= ~(1 << key.bit_pos)

    @classmethod
    def release_key(cls, key: CPCKey):
        cls._matrix[key.line] |= (1 << key.bit_pos)

    @classmethod
    def read_row(cls, row: int) -> int:
        return cls._matrix[row]