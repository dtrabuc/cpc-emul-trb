# Dans core/ppi.py
class PPI(IODevice):
    def __init__(self, crtc, psg):
        self._psg = psg
        self._crtc = crtc
        self._port_a_direction = IODirection.INPUT
        self._port_c_latched = 0
        self._cas_in = False
        self._tape_motor_on = False

    def write(self, port: int, value: int):
        masked = port & 0xF700
        if masked == 0xF400 and self._port_a_direction == IODirection.OUTPUT:
            self._psg.write(value)
        elif masked == 0xF600:
            self._port_c_latched = value
            self._apply_port_c_output(value)
        elif masked == 0xF700:
            # Config
            if value & 0x80 == 0:
                # Bit Set/Reset mode
                bit = (value >> 1) & 0x07
                if value & 0x01:
                    self._port_c_latched |= (1 << bit)
                else:
                    self._port_c_latched &= ~(1 << bit)
                self._apply_port_c_output(self._port_c_latched)
            else:
                self._port_a_direction = IODirection.INPUT if (value & 0x10) else IODirection.OUTPUT

    def read(self, port: int) -> int:
        masked = port & 0xF700
        if masked == 0xF400 and self._port_a_direction == IODirection.INPUT:
            return self._psg.read()
        elif masked == 0xF500:
            # Port B : Vsync, cassette, etc.
            cas_in = 0x80 if self._cas_in else 0x00
            vsync = 0x01 if self._crtc.vsync else 0x00
            return cas_in | 0x0E | (vsync << 4)  # etc.
        return 0xFF