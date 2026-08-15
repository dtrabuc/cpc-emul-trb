from enum import Enum
from .keyboard_state import KeyboardState
from .tape import TapeDrive

class IODirection(Enum):
    INPUT = 0
    OUTPUT = 1

class PPI:
    def __init__(self, crtc, psg, gate_array, tape: TapeDrive = None):
        self._crtc = crtc
        self._psg = psg
        self._gate_array = gate_array
        self._tape = tape
        self._keyboard = KeyboardState()
        self._port_a = 0xFF
        self._port_b = 0xFF
        self._port_c = 0xFF
        self._control = 0
        self._port_a_direction = IODirection.INPUT
        self._port_b_direction = IODirection.INPUT
        self._port_c_low_direction = IODirection.INPUT
        self._port_c_high_direction = IODirection.INPUT
        self._cas_in = False
        self._tape_motor_on = False

    def reset(self):
        self._port_a = 0xFF
        self._port_b = 0xFF
        self._port_c = 0xFF
        self._control = 0
        self._port_a_direction = IODirection.INPUT
        self._port_b_direction = IODirection.INPUT
        self._port_c_low_direction = IODirection.INPUT
        self._port_c_high_direction = IODirection.INPUT
        self._cas_in = False
        self._tape_motor_on = False

    def write(self, port: int, value: int):
        port_high = port & 0xF700
        port_low = port & 0x00FF

        if port_high == 0xF400:
            if port_low == 0x00:
                self._psg.write(value)
            elif port_low == 0x01:
                self._psg.set_address(value)
            if self._port_a_direction == IODirection.OUTPUT:
                self._port_a = value

        elif port_high == 0xF500:
            if self._port_b_direction == IODirection.OUTPUT:
                self._port_b = value

        elif port_high == 0xF600:
            if port_low == 0x00:
                self._port_c = value
                self._apply_port_c_output(value)

        elif port_high == 0xF700:
            self._control = value
            self._configure(value)

    def read(self, port: int) -> int:
        port_high = port & 0xF700
        port_low = port & 0x00FF

        if port_high == 0xF400:
            if self._port_a_direction == IODirection.INPUT:
                return self._psg.read()
            else:
                return self._port_a

        elif port_high == 0xF500:
            if self._port_b_direction == IODirection.INPUT:
                # Lecture du signal cassette depuis le TapeDrive
                if self._tape and self._tape.motor_on and self._tape.loaded:
                    self._cas_in = (self._tape.read_bit() == 1)
                cas_in = 0x80 if self._cas_in else 0x00
                vsync = 0x01 if self._crtc.vsync else 0x00
                return cas_in | 0x0E | (vsync << 4)
            else:
                return self._port_b

        elif port_high == 0xF600:
            return self._port_c

        elif port_high == 0xF700:
            return self._control

        return 0xFF

    def _configure(self, value: int):
        if value & 0x80:
            self._port_a_direction = IODirection.INPUT if (value & 0x10) else IODirection.OUTPUT
            self._port_b_direction = IODirection.INPUT if (value & 0x02) else IODirection.OUTPUT
            self._port_c_low_direction = IODirection.INPUT if (value & 0x01) else IODirection.OUTPUT
            self._port_c_high_direction = IODirection.INPUT if (value & 0x08) else IODirection.OUTPUT

    def _apply_port_c_output(self, value: int):
        row = value & 0x0F
        if row < 10:
            keyboard_data = self._keyboard.read_row(row)
            if self._port_a_direction == IODirection.INPUT:
                self._port_a = keyboard_data
        
        # Gestion du moteur cassette
        self._tape_motor_on = (value & 0x80) != 0
        if self._tape:
            self._tape.set_motor(self._tape_motor_on)

    def press_key(self, key: str) -> bool:
        if self._keyboard.press_azerty(key):
            if self._port_a_direction == IODirection.INPUT:
                row = self._port_c & 0x0F
                if row < 10:
                    self._port_a = self._keyboard.read_row(row)
            return True
        return False

    def release_key(self, key: str) -> bool:
        if self._keyboard.release_azerty(key):
            if self._port_a_direction == IODirection.INPUT:
                row = self._port_c & 0x0F
                if row < 10:
                    self._port_a = self._keyboard.read_row(row)
            return True
        return False