import z80

class Z80Wrapper:
    def __init__(self, memory, io_read_cb, io_write_cb):
        self.cpu = z80.Z80()
        self.memory = memory
        self.io_read = io_read_cb
        self.io_write = io_write_cb
        self.reset()
        
    def reset(self):
        self.cpu.reset()
        self.cpu.pc = 0x0000
        
    def step(self):
        """Exécute une instruction"""
        opcode = self.memory.read_byte(self.cpu.pc)
        self.cpu.step(opcode)
        
    def get_registers(self):
        return {
            'pc': self.cpu.pc,
            'sp': self.cpu.sp,
            'af': (self.cpu.a << 8) | self.cpu.f,
            'bc': (self.cpu.b << 8) | self.cpu.c,
            'de': (self.cpu.d << 8) | self.cpu.e,
            'hl': (self.cpu.h << 8) | self.cpu.l,
        }