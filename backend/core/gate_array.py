class GateArray:
    COLORS = [
        (0x00, 0x00, 0x00), (0x00, 0x00, 0x80), (0x00, 0x80, 0x00), (0x00, 0x80, 0x80),
        (0x80, 0x00, 0x00), (0x80, 0x00, 0x80), (0x80, 0x80, 0x00), (0x80, 0x80, 0x80),
        (0x00, 0x00, 0x00), (0x00, 0x00, 0xFF), (0x00, 0xFF, 0x00), (0x00, 0xFF, 0xFF),
        (0xFF, 0x00, 0x00), (0xFF, 0x00, 0xFF), (0xFF, 0xFF, 0x00), (0xFF, 0xFF, 0xFF),
    ]

    def __init__(self, memory, crtc):
        self.memory = memory
        self.crtc = crtc
        self.width = 80
        self.height = 25
        self.mode = 1
        self.screen = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.colors = [['#FFFFFF' for _ in range(self.width)] for _ in range(self.height)]
        self.cursor_x = 0
        self.cursor_y = 0
        self.interrupt_request = False
        self.frame_counter = 0
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
        if value & 0x80:
            self.mode = (value >> 4) & 0x03
        else:
            idx = (value >> 3) & 0x0F
            color = value & 0x07
            self._regs[idx] = color

    def tick(self, cycles: int):
        self.frame_counter += cycles
        if self.frame_counter >= 19968:
            self.frame_counter = 0
            self.interrupt_request = True
            self._render_frame()

    def _render_frame(self):
        char_ram_start = 0xC000
        for row in range(self.height):
            for col in range(self.width):
                addr = char_ram_start + (row * self.width + col)
                char_code = self.memory.read_byte(addr)
                if 32 <= char_code <= 126:
                    self.screen[row][col] = chr(char_code)
                else:
                    self.screen[row][col] = ' '
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
        return self.memory.read_byte(addr)