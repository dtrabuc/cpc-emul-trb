class CPCKey:
    def __init__(self, line: int, bit_pos: int):
        self.line = line
        self.bit_pos = bit_pos

class KeyboardState:
    # Touches principales
    A = CPCKey(8, 5)
    B = CPCKey(6, 6)
    C = CPCKey(7, 6)
    D = CPCKey(7, 5)
    E = CPCKey(7, 2)
    F = CPCKey(6, 5)
    G = CPCKey(6, 4)
    H = CPCKey(5, 4)
    I = CPCKey(4, 3)
    J = CPCKey(5, 5)
    K = CPCKey(4, 5)
    L = CPCKey(4, 4)
    M = CPCKey(4, 6)
    N = CPCKey(5, 6)
    O = CPCKey(4, 2)
    P = CPCKey(3, 3)
    Q = CPCKey(8, 3)
    R = CPCKey(6, 2)
    S = CPCKey(7, 4)
    T = CPCKey(6, 3)
    U = CPCKey(5, 2)
    V = CPCKey(6, 7)
    W = CPCKey(7, 3)
    X = CPCKey(7, 7)
    Y = CPCKey(5, 3)
    Z = CPCKey(8, 7)
    NUM0 = CPCKey(4, 0)
    NUM1 = CPCKey(8, 0)
    NUM2 = CPCKey(8, 1)
    NUM3 = CPCKey(7, 1)
    NUM4 = CPCKey(7, 0)
    NUM5 = CPCKey(6, 1)
    NUM6 = CPCKey(6, 0)
    NUM7 = CPCKey(5, 1)
    NUM8 = CPCKey(5, 0)
    NUM9 = CPCKey(4, 1)

    AZERTY_MAP = {
        'a': A, 'b': B, 'c': C, 'd': D, 'e': E, 'f': F, 'g': G,
        'h': H, 'i': I, 'j': J, 'k': K, 'l': L, 'm': M, 'n': N,
        'o': O, 'p': P, 'q': Q, 'r': R, 's': S, 't': T, 'u': U,
        'v': V, 'w': W, 'x': X, 'y': Y, 'z': Z,
        '0': NUM0, '1': NUM1, '2': NUM2, '3': NUM3, '4': NUM4,
        '5': NUM5, '6': NUM6, '7': NUM7, '8': NUM8, '9': NUM9,
        '²': NUM1, '&': NUM2, 'é': NUM3, '"': NUM4,
        "'": NUM5, '(': NUM6, '-': NUM7, 'è': NUM8,
        '_': NUM9, 'ç': NUM0,
    }

    _matrix = [0xFF] * 10

    @classmethod
    def press_key(cls, key: CPCKey):
        cls._matrix[key.line] &= ~(1 << key.bit_pos)

    @classmethod
    def release_key(cls, key: CPCKey):
        cls._matrix[key.line] |= (1 << key.bit_pos)

    @classmethod
    def read_row(cls, row: int) -> int:
        return cls._matrix[row] if 0 <= row < 10 else 0xFF

    @classmethod
    def press_azerty(cls, char: str) -> bool:
        key = cls.AZERTY_MAP.get(char.lower())
        if key:
            cls.press_key(key)
            return True
        return False

    @classmethod
    def release_azerty(cls, char: str) -> bool:
        key = cls.AZERTY_MAP.get(char.lower())
        if key:
            cls.release_key(key)
            return True
        return False