class PIO8255:
    def __init__(self):
        self.pa = 0xFF
        self.pb = 0xFF
        self.pc = 0xFF
        self.control = 0
        
    def reset(self):
        self.pa = 0xFF
        self.pb = 0xFF
        self.pc = 0xFF
        self.control = 0
        
    def write(self, addr, value):
        if addr == 0: self.pa = value
        elif addr == 1: self.pb = value
        elif addr == 2: self.pc = value
        elif addr == 3: self.control = value
        
    def read(self, addr):
        if addr == 0: return self.pa
        elif addr == 1: return self.pb
        elif addr == 2: return self.pc
        elif addr == 3: return self.control
        return 0xFF