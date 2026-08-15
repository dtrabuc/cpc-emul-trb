# core/keyboard_state.py
# Matrice de clavier du CPC 464 – 10 lignes × 8 colonnes
# Mapping AZERTY complet

class CPCKey:
    def __init__(self, line: int, bit_pos: int):
        self.line = line
        self.bit_pos = bit_pos

class KeyboardState:
    # Ligne 0 : F1 à F9
    F1 = CPCKey(0, 0)
    F2 = CPCKey(0, 1)
    F3 = CPCKey(0, 2)
    F4 = CPCKey(0, 3)
    F5 = CPCKey(0, 4)
    F6 = CPCKey(0, 5)
    F7 = CPCKey(0, 6)
    F8 = CPCKey(0, 7)
    F9 = CPCKey(1, 7)

    # Ligne 1 : chiffres
    NUM1 = CPCKey(1, 0)
    NUM2 = CPCKey(1, 1)
    NUM3 = CPCKey(1, 2)
    NUM4 = CPCKey(1, 3)
    NUM5 = CPCKey(1, 4)
    NUM6 = CPCKey(1, 5)
    NUM7 = CPCKey(1, 6)
    NUM8 = CPCKey(2, 0)
    NUM9 = CPCKey(2, 1)
    NUM0 = CPCKey(2, 2)

    # Ligne 2 : A, Z, E, R, T
    A = CPCKey(2, 3)
    Z = CPCKey(2, 4)
    E = CPCKey(2, 5)
    R = CPCKey(2, 6)
    T = CPCKey(2, 7)

    # Ligne 3 : Q, S, D, F, G, H, J, K
    Q = CPCKey(3, 0)
    S = CPCKey(3, 1)
    D = CPCKey(3, 2)
    F = CPCKey(3, 3)
    G = CPCKey(3, 4)
    H = CPCKey(3, 5)
    J = CPCKey(3, 6)
    K = CPCKey(3, 7)

    # Ligne 4 : L, M, ù, *
    L = CPCKey(4, 0)
    M = CPCKey(4, 1)
    U_GRAVE = CPCKey(4, 2)
    STAR = CPCKey(4, 3)

    # Ligne 5 : W, X, C, V, B, N, ?, .
    W = CPCKey(5, 0)
    X = CPCKey(5, 1)
    C = CPCKey(5, 2)
    V = CPCKey(5, 3)
    B = CPCKey(5, 4)
    N = CPCKey(5, 5)
    QUESTION = CPCKey(5, 6)
    DOT = CPCKey(5, 7)

    # Ligne 6 : ;, :, /, =, +, @, $
    SEMICOLON = CPCKey(6, 0)
    COLON = CPCKey(6, 1)
    SLASH = CPCKey(6, 2)
    EQUAL = CPCKey(6, 3)
    PLUS = CPCKey(6, 4)
    AT = CPCKey(6, 5)
    DOLLAR = CPCKey(6, 6)

    # Ligne 7 : Esc, Tab, Caps Lock, Shift
    ESC = CPCKey(7, 0)
    TAB = CPCKey(7, 1)
    CAPS_LOCK = CPCKey(7, 2)
    SHIFT_L = CPCKey(7, 3)
    SHIFT_R = CPCKey(7, 4)
    CTRL = CPCKey(7, 5)

    # Ligne 8 : Espace, Enter, Backspace, CLR, DEL
    SPACE = CPCKey(8, 0)
    ENTER = CPCKey(8, 1)
    BACKSPACE = CPCKey(8, 2)
    CLR = CPCKey(8, 3)
    DEL = CPCKey(8, 4)

    # Ligne 9 : flèches, Copy
    ARROW_UP = CPCKey(9, 0)
    ARROW_DOWN = CPCKey(9, 1)
    ARROW_LEFT = CPCKey(9, 2)
    ARROW_RIGHT = CPCKey(9, 3)
    COPY = CPCKey(9, 4)

    # Mapping complet AZERTY → CPCKey
    AZERTY_MAP = {
        'a': A, 'b': B, 'c': C, 'd': D, 'e': E, 'f': F,
        'g': G, 'h': H, 'i': I, 'j': J, 'k': K, 'l': L,
        'm': M, 'n': N, 'o': O, 'p': P, 'q': Q, 'r': R,
        's': S, 't': T, 'u': U, 'v': V, 'w': W, 'x': X,
        'y': Y, 'z': Z,
        '0': NUM0, '1': NUM1, '2': NUM2, '3': NUM3,
        '4': NUM4, '5': NUM5, '6': NUM6, '7': NUM7,
        '8': NUM8, '9': NUM9,
        '²': NUM1, '&': NUM2, 'é': NUM3, '"': NUM4,
        "'": NUM5, '(': NUM6, '-': NUM7, 'è': NUM8,
        '_': NUM9, 'ç': NUM0,
        'ù': U_GRAVE, '*': STAR,
        '?': QUESTION, '.': DOT,
        ';': SEMICOLON, ':': COLON,
        '/': SLASH, '=': EQUAL, '+': PLUS,
        '@': AT, '$': DOLLAR,
        'Esc': ESC, 'TAB': TAB, 'CAPS LOCK': CAPS_LOCK,
        'SHIFT': SHIFT_L, 'CTRL': CTRL,
        'SPACE': SPACE, 'ENTER': ENTER,
        'DEL': DEL, 'CLR': CLR,
        'ArrowUp': ARROW_UP, 'ArrowDown': ARROW_DOWN,
        'ArrowLeft': ARROW_LEFT, 'ArrowRight': ARROW_RIGHT,
        'COPY': COPY,
    }

    _matrix = [0xFF] * 10  # 10 lignes, chaque ligne = octet (8 bits)

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