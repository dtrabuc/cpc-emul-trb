# core/tape.py

class TapeDrive:
    def __init__(self):
        self.loaded = False
        self.filename = ""
        self.data = bytearray()
        self.position = 0
        self.playing = False
        self.motor_on = False
        self.counter = 0

    def load_tape(self, filename, data_bytes):
        self.filename = filename
        self.data = bytearray(data_bytes)
        self.position = 0
        self.counter = 0
        self.loaded = True
        self.playing = False

    def play(self):
        if self.loaded:
            self.playing = True

    def stop(self):
        self.playing = False

    def rewind(self):
        self.position = 0
        self.counter = 0

    def eject(self):
        self.__init__()

    def set_motor(self, state: bool):
        self.motor_on = state

    def read_bit(self):
        """Lit le bit courant pour le PPI/Cassette In."""
        if not (self.loaded and self.playing and self.motor_on):
            return 1
        if self.position >= len(self.data):
            self.playing = False
            return 1

        byte_idx = self.position // 8
        bit_idx = 7 - (self.position % 8)
        bit = (self.data[byte_idx] >> bit_idx) & 1
        
        self.position += 1
        self.counter = self.position // 8
        return bit