# core/crtc.py
# CRTC 6845 – Gestion des registres, timings, VSYNC, HSYNC

class CRTC6845:
    def __init__(self):
        # Registres 0-31
        self.regs = [0] * 32
        self.index = 0

        # État
        self.cursor_x = 0
        self.cursor_y = 0
        self.vsync = False
        self.hsync = False
        self.display_enabled = True

        # Compteurs internes
        self.char_counter = 0
        self.row_counter = 0
        self.frame_counter = 0

    def reset(self):
        self.regs = [0] * 32
        self.index = 0
        self.cursor_x = 0
        self.cursor_y = 0
        self.vsync = False
        self.hsync = False
        self.display_enabled = True
        self.char_counter = 0
        self.row_counter = 0
        self.frame_counter = 0

    def write(self, addr: int, value: int):
        if addr == 0:  # Index register
            self.index = value & 0x1F
        else:          # Data register
            self.regs[self.index] = value
            # Mise à jour du curseur (registres 14 et 15)
            if self.index == 14:
                self.cursor_x = (self.cursor_x & 0xFF00) | value
            elif self.index == 15:
                self.cursor_x = (self.cursor_x & 0x00FF) | (value << 8)
            elif self.index == 10:
                self.cursor_y = value

    def read(self, addr: int) -> int:
        if addr == 0:
            return self.index
        else:
            return self.regs[self.index] if self.index < 32 else 0

    def tick(self, cycles: int):
        """Simule le comptage des cycles pour générer VSYNC et HSYNC"""
        # Nombre de cycles par caractère (approximatif)
        chars_per_frame = 19968 // 25  # ~800 caractères par frame

        self.char_counter += cycles
        if self.char_counter >= chars_per_frame:
            self.char_counter = 0
            self.row_counter += 1

            if self.row_counter >= 25:
                self.row_counter = 0
                self.frame_counter += 1
                self.vsync = True
            else:
                self.vsync = False

        # HSYNC : toutes les 80 caractères
        self.hsync = (self.char_counter % 80) < 4