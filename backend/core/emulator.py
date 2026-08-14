from .z80_cpu import Z80CPU
from .memory import Memory
from .crtc import CRTC6845
from .gate_array import GateArray
from .pio import PIO8255

class Emulator:
    def __init__(self):
        self.memory = Memory()
        self.crtc = CRTC6845()
        self.gate_array = GateArray()
        self.pio = PIO8255()
        self.cpu = Z80CPU()
        self.cpu.memory = self.memory
        self.cpu.io_read = self.io_read
        self.cpu.io_write = self.io_write
        self.running = False
        
    def io_read(self, port):
        if 0x7F00 <= port <= 0x7F0F:
            return self.pio.read(port & 0x0F)
        elif 0x7F10 <= port <= 0x7F1F:
            return self.crtc.read(port & 0x01)
        elif 0x7F20 <= port <= 0x7F2F:
            return self.crtc.read(port & 0x01)
        elif 0x7F30 <= port <= 0x7F3F:
            return 0xFF  # AY-3-8912 (à implémenter)
        return 0xFF
        
    def io_write(self, port, value):
        if 0x7F00 <= port <= 0x7F0F:
            self.pio.write(port & 0x0F, value)
        elif 0x7F10 <= port <= 0x7F1F:
            self.crtc.write(port & 0x01, value)
        elif 0x7F20 <= port <= 0x7F2F:
            self.crtc.write(port & 0x01, value)
        elif 0x7F30 <= port <= 0x7F3F:
            pass  # AY-3-8912 (à implémenter)
            
def reset(self):
    self.memory.reset()
    self.crtc.reset()
    self.gate_array.reset()
    self.pio.reset()
    self.cpu.reset()
    self.running = True
    
    # Écran de démarrage CPC 464
    startup_text = [
        "Amstrad 64K Microcomputer <v1>",
        "(c) 1984 Amstrad Electronics",
        "this emulator created by Dydy 2026",
        "And Locomotive Software LTD",
        "",
        "BASIC 1.0",
        "",
        "Ready",
        "",
    ]
    
    # Afficher le texte sur l'écran (80x40)
    for row, line in enumerate(startup_text):
        for col, char in enumerate(line.ljust(80)):
            if col < 80 and row < 40:
                self.gate_array.screen[row][col] = char
                self.gate_array.colors[row][col] = '#ffff00'  # Jaune Amstrad
    
    # Curseur après "Ready"
    self.gate_array.cursor_x = len("Ready")
    self.gate_array.cursor_y = 8
        
    def step(self):
        if self.running:
            self.cpu.step()
            
    def load_roms(self, firmware_path, basic_path):
        with open(firmware_path, 'rb') as f:
            self.memory.load_rom(f.read(), 0x0000)
        with open(basic_path, 'rb') as f:
            self.memory.load_rom(f.read(), 0xC000)
            
    def get_screen_state(self):
        return self.gate_array.get_screen_buffer()