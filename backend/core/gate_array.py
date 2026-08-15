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

        # Registres du Gate Array (pour l'écriture)
        self._regs = [0] * 16

    def reset(self):
        self.screen = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.colors = [['#FFFFFF' for _ in range(self.width)] for _ in range(self.height)]
        self.cursor_x = 0
        self.cursor_y = 0
        self.interrupt_request = False
        self.frame_counter = 0
        self._regs = [0] * 16

    def write(self, value: int):
        """Écriture dans le Gate Array (port 0x7F00)"""
        # Bit 7 = sélection registre (0 = palette, 1 = mode)
        if value & 0x80:
            # Mode / configuration
            self.mode = (value >> 4) & 0x03
        else:
            # Palette (couleurs)
            idx = (value >> 3) & 0x0F
            color = value & 0x07
            self._regs[idx] = color

    def tick(self, cycles: int):
        """Appelé à chaque cycle CPU"""
        self.frame_counter += cycles

        # Interruption 50Hz (environ 19968 cycles)
        if self.frame_counter >= 19968:
            self.frame_counter = 0
            self.interrupt_request = True
            self._render_frame()

    def _render_frame(self):
        """Lit la RAM vidéo et construit l'écran"""
        # La RAM vidéo est toujours en &C000-&FFFF
        # Le texte VDU écrit à partir de &C000
        char_ram_start = 0xC000

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