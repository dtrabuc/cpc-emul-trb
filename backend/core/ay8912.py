import ay8910_wrapper

class AY8912Wrapper:
    def __init__(self):
        self.ay = ay8910_wrapper.AY8910(clock=1000000, sample_rate=44100)
        self.regs = [0] * 16
        self.index = 0
        
    def reset(self):
        self.ay.reset()
        self.regs = [0] * 16
        
    def write(self, addr, value):
        if addr == 0:  # Address
            self.index = value & 0x0F
        else:          # Data
            self.regs[self.index] = value
            self.ay.write_register(self.index, value)
            
    def read(self, addr):
        if addr == 0:
            return self.index
        else:
            return self.ay.read_register(self.index) if self.index < 16 else 0