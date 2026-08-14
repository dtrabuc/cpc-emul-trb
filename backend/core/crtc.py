class CRTC6845:
    def __init__(self):
        self.regs = [0] * 32
        self.index = 0
        self.cursor_x = 0
        self.cursor_y = 0
        
    def reset(self):
        self.regs = [0] * 32
        self.index = 0
        self.cursor_x = 0
        self.cursor_y = 0
        
    def write(self, addr, value):
        if addr == 0:
            self.index = value & 0x1F
        else:
            self.regs[self.index] = value
            if self.index == 10:
                self.cursor_y = value
                
    def read(self, addr):
        if addr == 0:
            return self.index
        return self.regs[self.index] if self.index < 32 else 0
        
    def tick(self):
        pass