# core/ppi.py
# PPI 8255 – Gestion des ports A, B, C, contrôle, clavier, cassette, PSG

from enum import Enum
from .io_device import IODevice
from .keyboard_state import KeyboardState

class IODirection(Enum):
    INPUT = 0
    OUTPUT = 1

class PPI(IODevice):
    def __init__(self, crtc, psg, gate_array):
        self._crtc = crtc
        self._psg = psg
        self._gate_array = gate_array
        self._keyboard = KeyboardState()

        # Registres internes
        self._port_a = 0xFF
        self._port_b = 0xFF
        self._port_c = 0xFF
        self._control = 0

        # Directions (0 = sortie, 1 = entrée)
        self._port_a_direction = IODirection.INPUT
        self._port_b_direction = IODirection.INPUT
        self._port_c_low_direction = IODirection.INPUT
        self._port_c_high_direction = IODirection.INPUT

        # État de la cassette
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

        # Port A (0xF4xx) – PSG et données clavier
        if port_high == 0xF400:
            if port_low == 0x00:      # F400 : écriture données PSG
                self._psg.write(value)
            elif port_low == 0x01:    # F401 : sélection registre PSG
                self._psg.set_address(value)
            if self._port_a_direction == IODirection.OUTPUT:
                self._port_a = value

        # Port B (0xF5xx) – VSYNC, cassette, jumpers
        elif port_high == 0xF500:
            if self._port_b_direction == IODirection.OUTPUT:
                self._port_b = value

        # Port C (0xF6xx) – sélection ligne clavier, moteur cassette
        elif port_high == 0xF600:
            if port_low == 0x00:
                self._port_c = value
                self._apply_port_c_output(value)

        # Registre de contrôle (0xF7xx)
        elif port_high == 0xF700:
            self._control = value
            self._configure(value)

    def read(self, port: int) -> int:
        port_high = port & 0xF700
        port_low = port & 0x00FF

        # Port A (0xF4xx) – lecture PSG ou données clavier
        if port_high == 0xF400:
            if self._port_a_direction == IODirection.INPUT:
                # Si le PSG est en lecture, on renvoie sa valeur
                return self._psg.read()
            else:
                return self._port_a

        # Port B (0xF5xx) – VSYNC, cassette, etc.
        elif port_high == 0xF500:
            if self._port_b_direction == IODirection.INPUT:
                cas_in = 0x80 if self._cas_in else 0x00
                vsync = 0x01 if self._crtc.vsync else 0x00
                # Bits 1-3 toujours à 1
                return cas_in | 0x0E | (vsync << 4)
            else:
                return self._port_b

        # Port C (0xF6xx)
        elif port_high == 0xF600:
            return self._port_c

        # Registre de contrôle (0xF7xx)
        elif port_high == 0xF700:
            return self._control

        return 0xFF

    def _configure(self, value: int):
        # Mode 0 : I/O de base (le seul utilisé par le CPC)
        if value & 0x80:
            # Port A
            self._port_a_direction = IODirection.INPUT if (value & 0x10) else IODirection.OUTPUT
            # Port B
            self._port_b_direction = IODirection.INPUT if (value & 0x02) else IODirection.OUTPUT
            # Port C bas (bits 0-3)
            self._port_c_low_direction = IODirection.INPUT if (value & 0x01) else IODirection.OUTPUT
            # Port C haut (bits 4-7)
            self._port_c_high_direction = IODirection.INPUT if (value & 0x08) else IODirection.OUTPUT

    def _apply_port_c_output(self, value: int):
        # Bits 0-3 : sélection ligne clavier
        row = value & 0x0F
        if row < 10:
            keyboard_data = self._keyboard.read_row(row)
            if self._port_a_direction == IODirection.INPUT:
                self._port_a = keyboard_data

        # Bit 7 : moteur cassette
        self._tape_motor_on = (value & 0x80) != 0

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