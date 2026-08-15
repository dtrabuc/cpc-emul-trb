# core/memory.py
# Mémoire 64KB + ROM banking (Firmware à 0x0000, BASIC à 0xC000)

class Memory:
    def __init__(self, size=0x10000):
        self.size = size
        self.ram = bytearray(size)
        self.roms = {}  # {adresse: data}

    def reset(self):
        self.ram = bytearray(self.size)

    def load_rom(self, data, address):
        self.roms[address] = data

    def read_byte(self, addr):
        # Vérifier si une ROM est présente à cette adresse
        for base, data in self.roms.items():
            if base <= addr < base + len(data):
                return data[addr - base]
        # Sinon, lire la RAM
        return self.ram[addr] if addr < self.size else 0xFF

    def write_byte(self, addr, value):
        if addr < self.size:
            self.ram[addr] = value