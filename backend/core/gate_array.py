# core/gate_array.py
# Gate Array Amstrad 40010 / 40009
# Gère les modes vidéo, les couleurs, les interruptions 50Hz

class GateArray:
    # Palette de 16 couleurs CPC
    COLORS = [
        (0x00, 0x00, 0x00),  # 0 : Noir
        (0x00, 0x00, 0x80),  # 1 : Bleu
        (0x00, 0x80, 0x00),  # 2 : Vert
        (0x00, 0x80, 0x80),  # 3 : Cyan
        (0x80, 0x00, 0x00),  # 4 : Rouge
        (0x80, 0x00, 0x80),  # 5 : Magenta
        (0x80, 0x80, 0x00),  # 6 : Jaune
        (0x80, 0x80, 0x80),  # 7 : Blanc
        (0x00, 0x00, 0x00),  # 8 : Noir (intensifié)
        (0x00, 0x00, 0xFF),  # 9 : Bleu clair
        (0x00, 0xFF, 0x00),  # A : Vert clair
        (0x00, 0xFF, 0xFF),  # B : Cyan clair
        (0xFF, 0x00, 0x00),  # C : Rouge clair
        (0xFF, 0x00, 0xFF),  # D : Magenta clair
        (0xFF, 0xFF, 0x00),  # E : Jaune clair
        (0xFF, 0xFF, 0xFF),  # F : Blanc clair
    ]

    def __init__(self, memory, crtc):
        self.memory = memory
        self.crtc = crtc
        self.width = 80   # Mode 1 par défaut
        self.height = 25
        self.mode = 1     # 0, 1, 2
        self.screen = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.colors = [['#FFFFFF' for _ in range(self.width)] for _ in range(self.height)]
        self.cursor_x = 0
        self.cursor_y = 0
        self.interrupt_request = False
        self.frame_counter = 0

    def reset(self):
        self.screen = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.colors = [['#FFFFFF' for _ in range(self.width)] for _ in range(self.height)]
        self.cursor_x = 0
        self.cursor_y = 0
        self.interrupt_request = False
        self.frame_counter = 0

    def tick(self, cycles: int):
        """Appelé à chaque cycle CPU"""
        self.frame_counter += cycles

        # Interruption 50Hz
        if self.frame_counter >= 19968:  # ~1/50ème de seconde
            self.frame_counter = 0
            self.interrupt_request = True
            self._render_frame()

    def _render_frame(self):
        """Lit la RAM vidéo et construit l'écran"""
        # RAM vidéo : 0xC000 à 0xFFFF
        # Les caractères sont stockés à 0xC000 + 0x800 (2KB)
        char_ram_start = 0xC000 + 0x800

        for row in range(self.height):
            for col in range(self.width):
                addr = char_ram_start + (row * self.width + col)
                char_code = self.memory.read_byte(addr)

                if 32 <= char_code <= 126:
                    self.screen[row][col] = chr(char_code)
                else:
                    self.screen[row][col] = ' '

                # Couleur : on lit l'attribut (simplifié)
                # Dans un vrai Gate Array, l'attribut est dans la RAM
                # On utilise le jaune par défaut pour le moment
                self.colors[row][col] = '#FFFF00'

    def get_screen_buffer(self):
        return {
            'chars': self.screen,
            'colors': self.colors,
            'cursor_x': self.cursor_x,
            'cursor_y': self.cursor_y,
            'mode': self.mode,
            'width': self.width,
            'height': self.height,
        }

    def read_video_ram(self, addr: int) -> int:
        """Lecture de la RAM vidéo (pour le CRTC)"""
        return self.memory.read_byte(addr)