class CRTC6845:
    def __init__(self):
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
        if addr == 0:
            self.index = value & 0x1F
        else:
            self.regs[self.index] = value
            if self.index == 14:
                self.cursor_x = (self.cursor_x & 0xFF00) | value
            elif self.index == 15:
                self.cursor_x = (self.cursor_x & 0x00FF) | (value << 8)
            elif self.index == 10:
                self.cursor_y = value

    def read(self, addr: int) -> int:
        if addr == 0:
            return self.index
        return self.regs[self.index] if self.index < 32 else 0

    def tick(self, cycles: int):
        chars_per_frame = 19968 // 25
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
        self.hsync = (self.char_counter % 80) < 4