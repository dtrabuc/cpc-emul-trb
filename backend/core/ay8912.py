# core/ay8912.py
# PSG AY-3-8912 – Son, clavier, ports I/O

class AY8912Wrapper:
    def __init__(self):
        # 16 registres
        self._regs = [0] * 16
        self._index = 0

        # État
        self._channel_a_freq = 0
        self._channel_b_freq = 0
        self._channel_c_freq = 0
        self._channel_a_amp = 0
        self._channel_b_amp = 0
        self._channel_c_amp = 0
        self._envelope_freq = 0
        self._envelope_shape = 0
        self._io_a = 0xFF
        self._io_b = 0xFF

    def reset(self):
        self._regs = [0] * 16
        self._index = 0
        self._channel_a_freq = 0
        self._channel_b_freq = 0
        self._channel_c_freq = 0
        self._channel_a_amp = 0
        self._channel_b_amp = 0
        self._channel_c_amp = 0
        self._envelope_freq = 0
        self._envelope_shape = 0
        self._io_a = 0xFF
        self._io_b = 0xFF

    def set_address(self, addr: int):
        self._index = addr & 0x0F

    def write(self, value: int):
        self._regs[self._index] = value & 0xFF
        # Mise à jour des paramètres en fonction du registre
        if self._index == 0:  # Channel A fine tune
            self._channel_a_freq = (self._channel_a_freq & 0xFF00) | value
        elif self._index == 1:  # Channel A coarse tune
            self._channel_a_freq = (self._channel_a_freq & 0x00FF) | (value << 8)
        elif self._index == 2:  # Channel B fine tune
            self._channel_b_freq = (self._channel_b_freq & 0xFF00) | value
        elif self._index == 3:  # Channel B coarse tune
            self._channel_b_freq = (self._channel_b_freq & 0x00FF) | (value << 8)
        elif self._index == 4:  # Channel C fine tune
            self._channel_c_freq = (self._channel_c_freq & 0xFF00) | value
        elif self._index == 5:  # Channel C coarse tune
            self._channel_c_freq = (self._channel_c_freq & 0x00FF) | (value << 8)
        elif self._index == 8:  # Channel A amplitude
            self._channel_a_amp = value & 0x1F
        elif self._index == 9:  # Channel B amplitude
            self._channel_b_amp = value & 0x1F
        elif self._index == 10: # Channel C amplitude
            self._channel_c_amp = value & 0x1F
        elif self._index == 11: # Envelope frequency
            self._envelope_freq = value
        elif self._index == 12: # Envelope shape
            self._envelope_shape = value
        elif self._index == 14: # I/O port A
            self._io_a = value
        elif self._index == 15: # I/O port B
            self._io_b = value

    def read(self) -> int:
        # Lecture des registres
        if self._index == 14:
            return self._io_a
        elif self._index == 15:
            return self._io_b
        return self._regs[self._index]