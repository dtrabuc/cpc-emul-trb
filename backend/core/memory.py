class Memory:
    """
    Modele memoire CPC464 avec overlay ROM/RAM correct.

    Sur un CPC reel, la ROM basse (firmware/OS, 0x0000-0x3FFF) et la ROM
    haute (BASIC ou ROM etendue, 0xC000-0xFFFF) sont des OVERLAYS : elles
    masquent la RAM en LECTURE quand elles sont activees, mais l'ECRITURE
    va TOUJOURS dans la RAM sous-jacente, meme quand la ROM est active.
    C'est le Gate Array (bits LowerROMEnabled/UpperROMEnabled) qui pilote
    ces deux flags via son registre de fonction 2 (cf. GateArray.py).
    """

    def __init__(self, size=0x10000):
        self.size = size
        self.ram = bytearray(size)
        self.roms = {}  # base_address -> bytes

        # Pilotes par le Gate Array (cf. gate_array.py -> ScreenModeROMConfig)
        self.lower_rom_enabled = True
        self.upper_rom_enabled = True

    def reset(self):
        self.ram = bytearray(self.size)
        self.lower_rom_enabled = True
        self.upper_rom_enabled = True

    def load_rom(self, data, address):
        self.roms[address] = data

    def _rom_at(self, addr):
        """Retourne (base, data) de la ROM couvrant addr, ou None."""
        for base, data in self.roms.items():
            if base <= addr < base + len(data):
                return base, data
        return None

    def read_byte(self, addr):
        addr &= 0xFFFF

        if addr < 0x4000 and self.lower_rom_enabled:
            hit = self._rom_at(0x0000)
            if hit:
                base, data = hit
                if base <= addr < base + len(data):
                    return data[addr - base]

        if addr >= 0xC000 and self.upper_rom_enabled:
            hit = self._rom_at(0xC000)
            if hit:
                base, data = hit
                if base <= addr < base + len(data):
                    return data[addr - base]

        return self.ram[addr] if addr < self.size else 0xFF

    def write_byte(self, addr, value):
        addr &= 0xFFFF
        # Les ecritures traversent toujours la ROM et atteignent la RAM.
        if addr < self.size:
            self.ram[addr] = value & 0xFF