# core/emulator.py
# Émulateur complet : CPU, mémoire, PPI, CRTC, GateArray, PSG
# Reset : maintient la ligne RESET haute, un appui la met à la masse

from .z80_cpu import Z80CPU
from .memory import Memory
from .crtc import CRTC6845
from .gate_array import GateArray
from .ppi import PPI
from .ay8912 import AY8912Wrapper
import threading

class Emulator:
    def __init__(self):
        self.memory = Memory()
        self.crtc = CRTC6845()
        self.gate_array = GateArray(self.memory, self.crtc)
        self.psg = AY8912Wrapper()
        self.ppi = PPI(self.crtc, self.psg, self.gate_array)
        self.cpu = Z80CPU()
        self.cpu.memory = self.memory
        self.cpu.io_read = self.io_read
        self.cpu.io_write = self.io_write
        self.running = False
        self.cpu_thread = None
        self._pending_cycles = 0
        self._cycle_lock = threading.Lock()
        self._cycle_event = threading.Event()

        # LED Power
        self.power_led = True

    def io_read(self, port):
        # Ports PPI : 0xF400 à 0xF7FF
        if 0xF400 <= port <= 0xF7FF:
            return self.ppi.read(port)
        return 0xFF

    def io_write(self, port, value):
        if 0xF400 <= port <= 0xF7FF:
            self.ppi.write(port, value)
        elif 0x7F00 <= port <= 0x7F0F:
            # Gate Array (écriture)
            self.gate_array.write(value)

    def reset(self):
        """Reset complet de la machine"""
        self.memory.reset()
        self.crtc.reset()
        self.gate_array.reset()
        self.psg.reset()
        self.ppi.reset()
        self.cpu.reset()
        self.running = True
        self._pending_cycles = 0

        # Charger les ROMs
        try:
            self.load_roms('roms/cpc464_fr.rom', 'roms/basic_1.0.rom')
        except FileNotFoundError:
            print("[EMULATOR] ROMs non trouvées")

        self._start_cpu_thread()

    def _start_cpu_thread(self):
        if self.cpu_thread is None or not self.cpu_thread.is_alive():
            self.cpu_thread = threading.Thread(target=self._cpu_loop, daemon=True)
            self.cpu_thread.start()

    def _cpu_loop(self):
        while self.running:
            with self._cycle_lock:
                if self._pending_cycles > 0:
                    cycles_to_execute = self._pending_cycles
                    self._pending_cycles = 0
                else:
                    cycles_to_execute = 16000

            cycles_done = 0
            while cycles_done < cycles_to_execute:
                cycles_done += self.cpu.step()

            self.crtc.tick(cycles_done)
            self.gate_array.tick(cycles_done)

            # --- Gestion de l'interruption 50Hz ---
            if self.gate_array.interrupt_request:
                self.gate_array.interrupt_request = False
                self.cpu.interrupt(0x01)  # Vecteur d'interruption (par défaut)

            if cycles_to_execute > 0:
                self._cycle_event.set()

    def dispatch_cycles(self, count: int):
        with self._cycle_lock:
            self._pending_cycles += count
            if self._pending_cycles > 16000000:
                self._pending_cycles = 16000000
        self._cycle_event.wait(timeout=0.05)

    def press_key(self, key: str):
        return self.ppi.press_key(key)

    def release_key(self, key: str):
        return self.ppi.release_key(key)

    def load_roms(self, firmware_path, basic_path):
        with open(firmware_path, 'rb') as f:
            self.memory.load_rom(f.read(), 0x0000)
        with open(basic_path, 'rb') as f:
            self.memory.load_rom(f.read(), 0xC000)

    def get_screen_state(self):
        return self.gate_array.get_screen_buffer()

    def get_status(self):
        return {
            'power_led': self.power_led,
            'cpu_reset': not self.cpu.reset_pin,
            'tape_motor': self.ppi._tape_motor_on,
            'running': self.running,
        }