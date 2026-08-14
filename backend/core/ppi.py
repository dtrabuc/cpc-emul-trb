from enum import Enum
from .io_device import IODevice
from .keyboard_state import KeyboardState

class IODirection(Enum):
    INPUT = 0
    OUTPUT = 1

class PPI(IODevice):
    def __init__(self, crtc, psg):
        self._psg = psg
        self._crtc = crtc
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

    def write(self, port: int, value: int):
        masked = port & 0xF700
        if masked == 0xF400:
            if self._port_a_direction == IODirection.OUTPUT:
                self._port_a = value
                self._psg.write(value)
        elif masked == 0xF600:
            self._port_c = value
            self._apply_port_c_output(value)
        elif masked == 0xF700:
            self._control = value
            self._configure(value)

    def read(self, port: int) -> int:
        masked = port & 0xF700
        if masked == 0xF400:
            if self._port_a_direction == IODirection.INPUT:
                return self._psg.read()
            else:
                return self._port_a
        elif masked == 0xF500:
            cas_in = 0x80 if self._cas_in else 0x00
            vsync = 0x01 if self._crtc.vsync else 0x00
            return cas_in | 0x0E | (vsync << 4)
        elif masked == 0xF600:
            return self._port_c
        elif masked == 0xF700:
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
            # Le PPI met automatiquement keyboard_data sur le port A
            # si le port A est en entrée
            if self._port_a_direction == IODirection.INPUT:
                self._port_a = keyboard_data
        self._tape_motor_on = (value & 0x80) != 0

    def press_key(self, key: str):
        """Appuie sur une touche AZERTY"""
        if KeyboardState.press_azerty(key):
            # Si le port A est en entrée, la touche est immédiatement lue
            if self._port_a_direction == IODirection.INPUT:
                row = self._port_c & 0x0F
                if row < 10:
                    self._port_a = self._keyboard.read_row(row)
            return True
        return False

    def release_key(self, key: str):
        """Relâche une touche AZERTY"""
        if KeyboardState.release_azerty(key):
            if self._port_a_direction == IODirection.INPUT:
                row = self._port_c & 0x0F
                if row < 10:
                    self._port_a = self._keyboard.read_row(row)
            return True
        return False