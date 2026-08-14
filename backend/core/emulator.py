from .z80_cpu import Z80CPU
from .memory import Memory
from .crtc import CRTC6845
from .gate_array import GateArray
from .pio import PIO8255

class Emulator:
    def __init__(self):
        self.memory = Memory()
        self.crtc = CRTC6845()
        self.gate_array = GateArray()
        self.pio = PIO8255()
        self.cpu = Z80CPU()
        self.cpu.memory = self.memory
        self.cpu.io_read = self.io_read
        self.cpu.io_write = self.io_write
        self.running = False

    def io_read(self, port):
        return 0xFF

    def io_write(self, port, value):
        pass

    def reset(self):
           # Vérifier que la ROM BASIC est chargée
    if 0xC000 in self.memory.roms:
        print("[EMULATOR] ROM BASIC chargée")
    else:
        print("[EMULATOR] ERREUR : ROM BASIC non chargée")
        self.memory.reset()
        self.crtc.reset()
        self.gate_array.reset()
        self.pio.reset()
        self.cpu.reset()
        self.running = True

        # --- ÉCRAN DE DÉMARRAGE CPC 464 ---
        startup_text = [
            "Amstrad 64K Microcomputer <v1>",
            "(c) 1984 Amstrad Electronics",
            "this emulator created by Dydy 2026",
            "And Locomotive Software LTD",
            "",
            "BASIC 1.0",
            "",
            "Ready",
            "",
        ]

        for row, line in enumerate(startup_text):
            for col, char in enumerate(line.ljust(80)):
                if col < 80 and row < 40:
                    self.gate_array.screen[row][col] = char
                    self.gate_array.colors[row][col] = '#ffff00'

        self.gate_array.cursor_x = len("Ready")
        self.gate_array.cursor_y = 8

    def step(self):
        if self.running:
            self.cpu.step()

    def get_screen_state(self):
        return self.gate_array.get_screen_buffer()

        class KeyPressView(APIView):
    def post(self, request):
        key = request.data.get('key')
        # Exécuter quelques cycles CPU pour traiter la touche
        for _ in range(100):
            emulator.step()
        return Response({'status': 'ok'})