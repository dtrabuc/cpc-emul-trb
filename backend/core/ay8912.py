class AY8912Wrapper:
    def __init__(self):
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
        if self._index == 0:
            self._channel_a_freq = (self._channel_a_freq & 0xFF00) | value
        elif self._index == 1:
            self._channel_a_freq = (self._channel_a_freq & 0x00FF) | (value << 8)
        elif self._index == 2:
            self._channel_b_freq = (self._channel_b_freq & 0xFF00) | value
        elif self._index == 3:
            self._channel_b_freq = (self._channel_b_freq & 0x00FF) | (value << 8)
        elif self._index == 4:
            self._channel_c_freq = (self._channel_c_freq & 0xFF00) | value
        elif self._index == 5:
            self._channel_c_freq = (self._channel_c_freq & 0x00FF) | (value << 8)
        elif self._index == 8:
            self._channel_a_amp = value & 0x1F
        elif self._index == 9:
            self._channel_b_amp = value & 0x1F
        elif self._index == 10:
            self._channel_c_amp = value & 0x1F
        elif self._index == 11:
            self._envelope_freq = value
        elif self._index == 12:
            self._envelope_shape = value
        elif self._index == 14:
            self._io_a = value
        elif self._index == 15:
            self._io_b = value

    def read(self) -> int:
        if self._index == 14:
            return self._io_a
        elif self._index == 15:
            return self._io_b
        return self._regs[self._index]