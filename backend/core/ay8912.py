# core/ay8912.py
# Implémentation simplifiée de l'AY-3-8912 (stockage des registres)

class AY8912Wrapper:
    def __init__(self):
        self._regs = [0] * 16
        self._index = 0

    def reset(self):
        self._regs = [0] * 16
        self._index = 0

    def write(self, value: int):
        if self._index < 16:
            self._regs[self._index] = value & 0xFF

    def read(self) -> int:
        return self._regs[self._index] if self._index < 16 else 0xFF

    def set_address(self, addr: int):
        self._index = addr & 0x0F