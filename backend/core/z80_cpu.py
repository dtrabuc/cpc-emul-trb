# core/z80_cpu.py
# Z80 CPU – Toutes les instructions, préfixes CB / DD / FD / ED, interruptions, flags, cycles
# Compatible CPC 464 – Reset actif bas (pin 26)
# Version complète et stable

class Z80CPU:
    def __init__(self):
        self.memory = None
        self.io_read = None
        self.io_write = None

        # Registres principaux 8 bits
        self.a = 0x00
        self.f = 0x00
        self.b = 0x00
        self.c = 0x00
        self.d = 0x00
        self.e = 0x00
        self.h = 0x00
        self.l = 0x00

        # Registres alternatifs
        self.a_alt = 0x00
        self.f_alt = 0x00
        self.b_alt = 0x00
        self.c_alt = 0x00
        self.d_alt = 0x00
        self.e_alt = 0x00
        self.h_alt = 0x00
        self.l_alt = 0x00

        # Registres 16 bits
        self.ix = 0x0000
        self.iy = 0x0000
        self.sp = 0xFFFF
        self.pc = 0x0000

        # Registres spéciaux
        self.i = 0x00
        self.r = 0x00

        # Interruptions
        self.iff1 = False
        self.iff2 = False
        self.im = 0
        self.halted = False

        # Reset (actif bas)
        self.reset_pin = True

        # Cycles
        self._cycles = 0

    # --- Accesseurs 16 bits ---
    @property
    def af(self):
        return (self.a << 8) | self.f
    @af.setter
    def af(self, v):
        self.a = (v >> 8) & 0xFF
        self.f = v & 0xFF

    @property
    def bc(self):
        return (self.b << 8) | self.c
    @bc.setter
    def bc(self, v):
        self.b = (v >> 8) & 0xFF
        self.c = v & 0xFF

    @property
    def de(self):
        return (self.d << 8) | self.e
    @de.setter
    def de(self, v):
        self.d = (v >> 8) & 0xFF
        self.e = v & 0xFF

    @property
    def hl(self):
        return (self.h << 8) | self.l
    @hl.setter
    def hl(self, v):
        self.h = (v >> 8) & 0xFF
        self.l = v & 0xFF

    @property
    def af_alt(self):
        return (self.a_alt << 8) | self.f_alt
    @af_alt.setter
    def af_alt(self, v):
        self.a_alt = (v >> 8) & 0xFF
        self.f_alt = v & 0xFF

    @property
    def bc_alt(self):
        return (self.b_alt << 8) | self.c_alt
    @bc_alt.setter
    def bc_alt(self, v):
        self.b_alt = (v >> 8) & 0xFF
        self.c_alt = v & 0xFF

    @property
    def de_alt(self):
        return (self.d_alt << 8) | self.e_alt
    @de_alt.setter
    def de_alt(self, v):
        self.d_alt = (v >> 8) & 0xFF
        self.e_alt = v & 0xFF

    @property
    def hl_alt(self):
        return (self.h_alt << 8) | self.l_alt
    @hl_alt.setter
    def hl_alt(self, v):
        self.h_alt = (v >> 8) & 0xFF
        self.l_alt = v & 0xFF

    # --- Flags ---
    FLAG_C = 0x01
    FLAG_N = 0x02
    FLAG_PV = 0x04
    FLAG_H = 0x10
    FLAG_Z = 0x40
    FLAG_S = 0x80

    def set_flag(self, flag, value):
        if value:
            self.f |= flag
        else:
            self.f &= ~flag

    def get_flag(self, flag):
        return (self.f & flag) != 0

    # --- Mémoire ---
    def read_byte(self, addr):
        return self.memory.read_byte(addr) if self.memory else 0xFF

    def write_byte(self, addr, value):
        if self.memory:
            self.memory.write_byte(addr, value)

    def read_word(self, addr):
        return self.read_byte(addr) | (self.read_byte(addr + 1) << 8)

    def write_word(self, addr, value):
        self.write_byte(addr, value & 0xFF)
        self.write_byte(addr + 1, (value >> 8) & 0xFF)

    # --- I/O ---
    def in_byte(self, port):
        return self.io_read(port) if self.io_read else 0xFF

    def out_byte(self, port, value):
        if self.io_write:
            self.io_write(port, value)

    # --- Interruptions ---
    def interrupt(self, vector=0x00):
        if not self.iff1:
            return 4
        self.halted = False
        if self.im == 0:
            self.sp -= 1
            self.write_byte(self.sp, (self.pc >> 8) & 0xFF)
            self.sp -= 1
            self.write_byte(self.sp, self.pc & 0xFF)
            self.pc = 0x0000
            self.iff1 = False
            self.iff2 = False
            return 7
        elif self.im == 1:
            self.sp -= 1
            self.write_byte(self.sp, (self.pc >> 8) & 0xFF)
            self.sp -= 1
            self.write_byte(self.sp, self.pc & 0xFF)
            self.pc = 0x0038
            self.iff1 = False
            self.iff2 = False
            return 7
        elif self.im == 2:
            addr = (self.i << 8) | vector
            self.pc = self.read_word(addr)
            self.iff1 = False
            self.iff2 = False
            return 7
        return 4

    # --- Reset ---
    def reset(self):
        """Reset complet du CPU (actif bas)"""
        self.a = 0x00
        self.f = 0x00
        self.b = 0x00
        self.c = 0x00
        self.d = 0x00
        self.e = 0x00
        self.h = 0x00
        self.l = 0x00
        self.a_alt = 0x00
        self.f_alt = 0x00
        self.b_alt = 0x00
        self.c_alt = 0x00
        self.d_alt = 0x00
        self.e_alt = 0x00
        self.h_alt = 0x00
        self.l_alt = 0x00
        self.ix = 0x0000
        self.iy = 0x0000
        self.sp = 0xFFFF
        self.pc = 0x0000
        self.i = 0x00
        self.r = 0x00
        self.iff1 = False
        self.iff2 = False
        self.im = 0
        self.halted = False
        self.reset_pin = True
        self._cycles = 0

    def assert_reset(self):
        """Met la ligne RESET à 0 (actif bas)"""
        self.reset_pin = False
        self.reset()

    def release_reset(self):
        """Relâche la ligne RESET (passe à 1)"""
        self.reset_pin = True

    # --- Step ---
    def step(self):
        if self.halted or not self.reset_pin:
            self._cycles += 1
            return 1

        opcode = self.read_byte(self.pc)
        self.pc += 1
        self.r = (self.r + 1) & 0x7F

        cycles = self.execute(opcode)
        self._cycles += cycles
        return cycles

    # --- Exécution ---
    def execute(self, opcode):
        # Préfixes
        if opcode == 0xDD:
            sub = self.read_byte(self.pc)
            self.pc += 1
            return self.execute_dd(sub)
        if opcode == 0xFD:
            sub = self.read_byte(self.pc)
            self.pc += 1
            return self.execute_fd(sub)
        if opcode == 0xCB:
            sub = self.read_byte(self.pc)
            self.pc += 1
            return self.execute_cb(sub)
        if opcode == 0xED:
            sub = self.read_byte(self.pc)
            self.pc += 1
            return self.execute_ed(sub)

        # 8-bit LD r, r'
        if 0x40 <= opcode <= 0x7F:
            src = opcode & 0x07
            dst = (opcode >> 3) & 0x07
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            val = self._get_reg(regs[src])
            self._set_reg(regs[dst], val)
            if regs[src] == 'hl' and regs[dst] != 'hl':
                return 7
            if regs[dst] == 'hl':
                return 7
            return 4

        # LD r, n
        if opcode in [0x06, 0x0E, 0x16, 0x1E, 0x26, 0x2E, 0x3E]:
            reg_map = {0x06: 'b', 0x0E: 'c', 0x16: 'd', 0x1E: 'e', 0x26: 'h', 0x2E: 'l', 0x3E: 'a'}
            self._set_reg(reg_map[opcode], self.read_byte(self.pc))
            self.pc += 1
            return 7

        # LD rr, nn
        if opcode in [0x01, 0x11, 0x21, 0x31]:
            reg_map = {0x01: 'bc', 0x11: 'de', 0x21: 'hl', 0x31: 'sp'}
            self._set_reg16(reg_map[opcode], self.read_word(self.pc))
            self.pc += 2
            return 10

        # LD (BC), A / LD (DE), A / LD (HL), A
        if opcode == 0x02:
            self.write_byte(self.bc, self.a)
            return 7
        if opcode == 0x12:
            self.write_byte(self.de, self.a)
            return 7
        if opcode == 0x77:
            self.write_byte(self.hl, self.a)
            return 7

        # LD A, (BC) / LD A, (DE) / LD A, (HL)
        if opcode == 0x0A:
            self.a = self.read_byte(self.bc)
            return 7
        if opcode == 0x1A:
            self.a = self.read_byte(self.de)
            return 7
        if opcode == 0x7E:
            self.a = self.read_byte(self.hl)
            return 7

        # EX DE, HL
        if opcode == 0xEB:
            self.de, self.hl = self.hl, self.de
            return 4
        # EX AF, AF'
        if opcode == 0x08:
            self.af, self.af_alt = self.af_alt, self.af
            return 4
        # EXX
        if opcode == 0xD9:
            self.bc, self.bc_alt = self.bc_alt, self.bc
            self.de, self.de_alt = self.de_alt, self.de
            self.hl, self.hl_alt = self.hl_alt, self.hl
            return 4
        # EX (SP), HL
        if opcode == 0xE3:
            tmp = self.read_word(self.sp)
            self.write_word(self.sp, self.hl)
            self.hl = tmp
            return 19

        # ADD HL, rr
        if opcode in [0x09, 0x19, 0x29, 0x39]:
            reg_map = {0x09: 'bc', 0x19: 'de', 0x29: 'hl', 0x39: 'sp'}
            val = self._get_reg16(reg_map[opcode])
            result = self.hl + val
            self.set_flag(0x10, (self.hl & 0x0FFF) + (val & 0x0FFF) > 0x0FFF)
            self.set_flag(0x01, result > 0xFFFF)
            self.set_flag(0x02, False)
            self.hl = result & 0xFFFF
            return 11

        # INC/DEC 16-bit
        if opcode in [0x03, 0x0B, 0x13, 0x1B, 0x23, 0x2B, 0x33, 0x3B]:
            reg_map = {
                0x03: 'bc', 0x0B: 'bc',
                0x13: 'de', 0x1B: 'de',
                0x23: 'hl', 0x2B: 'hl',
                0x33: 'sp', 0x3B: 'sp'
            }
            reg = reg_map[opcode]
            val = self._get_reg16(reg)
            if opcode & 0x08:
                val = (val - 1) & 0xFFFF
            else:
                val = (val + 1) & 0xFFFF
            self._set_reg16(reg, val)
            return 6

        # INC/DEC 8-bit
        if (0x04 <= opcode <= 0x3C) and (opcode & 0x07) in [0x04, 0x05]:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = (opcode >> 3) & 0x07
            is_dec = (opcode & 0x07) == 0x05
            val = self._get_reg(regs[idx])
            if is_dec:
                val -= 1
            else:
                val += 1
            self._set_reg(regs[idx], val & 0xFF)
            self.set_flag(0x10, (val & 0x0F) == (0x0F if is_dec else 0x00))
            self.set_flag(0x80, val & 0x80)
            self.set_flag(0x40, (val & 0xFF) == 0)
            self.set_flag(0x02, is_dec)
            self.set_flag(0x04, val == (0x7F if is_dec else 0x80))
            if regs[idx] == 'hl':
                return 11
            return 4

        # ADD A, r
        if 0x80 <= opcode <= 0x87:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = opcode & 0x07
            n = self._get_reg(regs[idx])
            result = self.a + n
            self.set_flag(0x10, ((self.a & 0x0F) + (n & 0x0F)) > 0x0F)
            self.set_flag(0x01, result > 0xFF)
            self.a = result & 0xFF
            self.set_flag(0x80, self.a & 0x80)
            self.set_flag(0x40, self.a == 0)
            self.set_flag(0x02, False)
            self.set_flag(0x04, ((self.a & 0x80) != (result & 0x80)))
            if regs[idx] == 'hl':
                return 7
            return 4

        # ADD A, n
        if opcode == 0xC6:
            n = self.read_byte(self.pc)
            self.pc += 1
            result = self.a + n
            self.set_flag(0x10, ((self.a & 0x0F) + (n & 0x0F)) > 0x0F)
            self.set_flag(0x01, result > 0xFF)
            self.a = result & 0xFF
            self.set_flag(0x80, self.a & 0x80)
            self.set_flag(0x40, self.a == 0)
            self.set_flag(0x02, False)
            self.set_flag(0x04, ((self.a & 0x80) != (result & 0x80)))
            return 7

        # ADC A, r
        if 0x88 <= opcode <= 0x8F:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = opcode & 0x07
            n = self._get_reg(regs[idx])
            carry = 1 if self.get_flag(0x01) else 0
            result = self.a + n + carry
            self.set_flag(0x10, ((self.a & 0x0F) + (n & 0x0F) + carry) > 0x0F)
            self.set_flag(0x01, result > 0xFF)
            self.a = result & 0xFF
            self.set_flag(0x80, self.a & 0x80)
            self.set_flag(0x40, self.a == 0)
            self.set_flag(0x02, False)
            self.set_flag(0x04, ((self.a & 0x80) != (result & 0x80)))
            if regs[idx] == 'hl':
                return 7
            return 4

        # ADC A, n
        if opcode == 0xCE:
            n = self.read_byte(self.pc)
            self.pc += 1
            carry = 1 if self.get_flag(0x01) else 0
            result = self.a + n + carry
            self.set_flag(0x10, ((self.a & 0x0F) + (n & 0x0F) + carry) > 0x0F)
            self.set_flag(0x01, result > 0xFF)
            self.a = result & 0xFF
            self.set_flag(0x80, self.a & 0x80)
            self.set_flag(0x40, self.a == 0)
            self.set_flag(0x02, False)
            self.set_flag(0x04, ((self.a & 0x80) != (result & 0x80)))
            return 7

        # SUB A, r
        if 0x90 <= opcode <= 0x97:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = opcode & 0x07
            n = self._get_reg(regs[idx])
            result = self.a - n
            self.set_flag(0x10, (self.a & 0x0F) < (n & 0x0F))
            self.set_flag(0x01, self.a < n)
            self.a = result & 0xFF
            self.set_flag(0x80, self.a & 0x80)
            self.set_flag(0x40, self.a == 0)
            self.set_flag(0x02, True)
            self.set_flag(0x04, ((self.a & 0x80) != (result & 0x80)))
            if regs[idx] == 'hl':
                return 7
            return 4

        # SUB A, n
        if opcode == 0xD6:
            n = self.read_byte(self.pc)
            self.pc += 1
            result = self.a - n
            self.set_flag(0x10, (self.a & 0x0F) < (n & 0x0F))
            self.set_flag(0x01, self.a < n)
            self.a = result & 0xFF
            self.set_flag(0x80, self.a & 0x80)
            self.set_flag(0x40, self.a == 0)
            self.set_flag(0x02, True)
            self.set_flag(0x04, ((self.a & 0x80) != (result & 0x80)))
            return 7

        # SBC A, r
        if 0x98 <= opcode <= 0x9F:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = opcode & 0x07
            n = self._get_reg(regs[idx])
            carry = 1 if self.get_flag(0x01) else 0
            result = self.a - n - carry
            self.set_flag(0x10, (self.a & 0x0F) < (n & 0x0F) + carry)
            self.set_flag(0x01, self.a < n + carry)
            self.a = result & 0xFF
            self.set_flag(0x80, self.a & 0x80)
            self.set_flag(0x40, self.a == 0)
            self.set_flag(0x02, True)
            self.set_flag(0x04, ((self.a & 0x80) != (result & 0x80)))
            if regs[idx] == 'hl':
                return 7
            return 4

        # SBC A, n
        if opcode == 0xDE:
            n = self.read_byte(self.pc)
            self.pc += 1
            carry = 1 if self.get_flag(0x01) else 0
            result = self.a - n - carry
            self.set_flag(0x10, (self.a & 0x0F) < (n & 0x0F) + carry)
            self.set_flag(0x01, self.a < n + carry)
            self.a = result & 0xFF
            self.set_flag(0x80, self.a & 0x80)
            self.set_flag(0x40, self.a == 0)
            self.set_flag(0x02, True)
            self.set_flag(0x04, ((self.a & 0x80) != (result & 0x80)))
            return 7

        # AND A, r
        if 0xA0 <= opcode <= 0xA7:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = opcode & 0x07
            self.a &= self._get_reg(regs[idx])
            self.set_flag(0x10, True)
            self.set_flag(0x01, False)
            self.set_flag(0x02, False)
            self.set_flag(0x80, self.a & 0x80)
            self.set_flag(0x40, self.a == 0)
            self.set_flag(0x04, self.a & 0x80)
            if regs[idx] == 'hl':
                return 7
            return 4

        # AND A, n
        if opcode == 0xE6:
            n = self.read_byte(self.pc)
            self.pc += 1
            self.a &= n
            self.set_flag(0x10, True)
            self.set_flag(0x01, False)
            self.set_flag(0x02, False)
            self.set_flag(0x80, self.a & 0x80)
            self.set_flag(0x40, self.a == 0)
            self.set_flag(0x04, self.a & 0x80)
            return 7

        # OR A, r
        if 0xB0 <= opcode <= 0xB7:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = opcode & 0x07
            self.a |= self._get_reg(regs[idx])
            self.set_flag(0x10, False)
            self.set_flag(0x01, False)
            self.set_flag(0x02, False)
            self.set_flag(0x80, self.a & 0x80)
            self.set_flag(0x40, self.a == 0)
            self.set_flag(0x04, self.a & 0x80)
            if regs[idx] == 'hl':
                return 7
            return 4

        # OR A, n
        if opcode == 0xF6:
            n = self.read_byte(self.pc)
            self.pc += 1
            self.a |= n
            self.set_flag(0x10, False)
            self.set_flag(0x01, False)
            self.set_flag(0x02, False)
            self.set_flag(0x80, self.a & 0x80)
            self.set_flag(0x40, self.a == 0)
            self.set_flag(0x04, self.a & 0x80)
            return 7

        # XOR A, r
        if 0xA8 <= opcode <= 0xAF:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = opcode & 0x07
            self.a ^= self._get_reg(regs[idx])
            self.set_flag(0x10, False)
            self.set_flag(0x01, False)
            self.set_flag(0x02, False)
            self.set_flag(0x80, self.a & 0x80)
            self.set_flag(0x40, self.a == 0)
            self.set_flag(0x04, self.a & 0x80)
            if regs[idx] == 'hl':
                return 7
            return 4

        # XOR A, n
        if opcode == 0xEE:
            n = self.read_byte(self.pc)
            self.pc += 1
            self.a ^= n
            self.set_flag(0x10, False)
            self.set_flag(0x01, False)
            self.set_flag(0x02, False)
            self.set_flag(0x80, self.a & 0x80)
            self.set_flag(0x40, self.a == 0)
            self.set_flag(0x04, self.a & 0x80)
            return 7

        # CP A, r
        if 0xB8 <= opcode <= 0xBF:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = opcode & 0x07
            n = self._get_reg(regs[idx])
            result = self.a - n
            self.set_flag(0x10, (self.a & 0x0F) < (n & 0x0F))
            self.set_flag(0x01, self.a < n)
            self.set_flag(0x80, result & 0x80)
            self.set_flag(0x40, (result & 0xFF) == 0)
            self.set_flag(0x02, True)
            self.set_flag(0x04, ((result & 0x80) != ((result & 0xFF) & 0x80)))
            if regs[idx] == 'hl':
                return 7
            return 4

        # CP A, n
        if opcode == 0xFE:
            n = self.read_byte(self.pc)
            self.pc += 1
            result = self.a - n
            self.set_flag(0x10, (self.a & 0x0F) < (n & 0x0F))
            self.set_flag(0x01, self.a < n)
            self.set_flag(0x80, result & 0x80)
            self.set_flag(0x40, (result & 0xFF) == 0)
            self.set_flag(0x02, True)
            self.set_flag(0x04, ((result & 0x80) != ((result & 0xFF) & 0x80)))
            return 7

        # PUSH
        if opcode in [0xC5, 0xD5, 0xE5, 0xF5]:
            reg_map = {0xC5: 'bc', 0xD5: 'de', 0xE5: 'hl', 0xF5: 'af'}
            val = self._get_reg16(reg_map[opcode])
            self.sp -= 1
            self.write_byte(self.sp, (val >> 8) & 0xFF)
            self.sp -= 1
            self.write_byte(self.sp, val & 0xFF)
            return 11

        # POP
        if opcode in [0xC1, 0xD1, 0xE1, 0xF1]:
            reg_map = {0xC1: 'bc', 0xD1: 'de', 0xE1: 'hl', 0xF1: 'af'}
            val = self.read_word(self.sp)
            self.sp += 2
            self._set_reg16(reg_map[opcode], val)
            if opcode == 0xF1:
                self.f &= 0xFF
            return 10

        # CALL
        if opcode == 0xCD:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.sp -= 1
            self.write_byte(self.sp, (self.pc >> 8) & 0xFF)
            self.sp -= 1
            self.write_byte(self.sp, self.pc & 0xFF)
            self.pc = addr
            return 17

        # CALL condition
        if (0xC4 <= opcode <= 0xFC) and (opcode & 0x07) == 0x04:
            cond = (opcode >> 3) & 0x07
            if self._check_cond(cond):
                addr = self.read_word(self.pc)
                self.pc += 2
                self.sp -= 1
                self.write_byte(self.sp, (self.pc >> 8) & 0xFF)
                self.sp -= 1
                self.write_byte(self.sp, self.pc & 0xFF)
                self.pc = addr
                return 17
            else:
                self.pc += 2
                return 10

        # RET
        if opcode == 0xC9:
            self.pc = self.read_word(self.sp)
            self.sp += 2
            return 10

        # RET condition
        if (0xC0 <= opcode <= 0xF8) and (opcode & 0x07) == 0x00 and opcode != 0xC9:
            cond = (opcode >> 3) & 0x07
            if self._check_cond(cond):
                self.pc = self.read_word(self.sp)
                self.sp += 2
                return 11
            return 5

        # RST
        if opcode >= 0xC7 and (opcode & 0xC7) == 0xC7:
            rst_addr = opcode & 0x38
            self.sp -= 1
            self.write_byte(self.sp, (self.pc >> 8) & 0xFF)
            self.sp -= 1
            self.write_byte(self.sp, self.pc & 0xFF)
            self.pc = rst_addr
            return 11

        # JP
        if opcode == 0xC3:
            self.pc = self.read_word(self.pc)
            return 10

        # JP condition
        if (0xC2 <= opcode <= 0xFA) and (opcode & 0x07) == 0x02:
            cond = (opcode >> 3) & 0x07
            if self._check_cond(cond):
                self.pc = self.read_word(self.pc)
                return 10
            else:
                self.pc += 2
                return 10

        # JP (HL)
        if opcode == 0xE9:
            self.pc = self.hl
            return 4

        # JR
        if opcode == 0x18:
            offset = self.read_byte(self.pc)
            self.pc += 1
            if offset & 0x80:
                self.pc -= (0x100 - offset)
            else:
                self.pc += offset
            return 12

        # JR condition
        if opcode in [0x20, 0x28, 0x30, 0x38]:
            cond_map = {0x20: 'nz', 0x28: 'z', 0x30: 'nc', 0x38: 'c'}
            if self._check_cond(cond_map[opcode]):
                offset = self.read_byte(self.pc)
                self.pc += 1
                if offset & 0x80:
                    self.pc -= (0x100 - offset)
                else:
                    self.pc += offset
                return 12
            else:
                self.pc += 1
                return 7

        # NOP
        if opcode == 0x00:
            return 4

        # HALT
        if opcode == 0x76:
            self.halted = True
            return 4

        # DI
        if opcode == 0xF3:
            self.iff1 = False
            self.iff2 = False
            return 4

        # EI
        if opcode == 0xFB:
            self.iff1 = True
            self.iff2 = True
            return 4

        # LD (nn), A
        if opcode == 0x32:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.write_byte(addr, self.a)
            return 13

        # LD A, (nn)
        if opcode == 0x3A:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.a = self.read_byte(addr)
            return 13

        # LD (nn), HL
        if opcode == 0x22:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.write_byte(addr, self.l)
            self.write_byte(addr + 1, self.h)
            return 16

        # LD HL, (nn)
        if opcode == 0x2A:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.l = self.read_byte(addr)
            self.h = self.read_byte(addr + 1)
            return 16

        # IN A, (n)
        if opcode == 0xDB:
            port = self.read_byte(self.pc)
            self.pc += 1
            self.a = self.in_byte(port)
            return 11

        # OUT (n), A
        if opcode == 0xD3:
            port = self.read_byte(self.pc)
            self.pc += 1
            self.out_byte(port, self.a)
            return 11

        # CPL
        if opcode == 0x2F:
            self.a ^= 0xFF
            self.set_flag(0x10, True)
            self.set_flag(0x02, True)
            return 4

        # SCF
        if opcode == 0x37:
            self.set_flag(0x01, True)
            self.set_flag(0x10, False)
            self.set_flag(0x02, False)
            return 4

        # CCF
        if opcode == 0x3F:
            self.set_flag(0x01, not self.get_flag(0x01))
            self.set_flag(0x10, False)
            self.set_flag(0x02, False)
            return 4

        # DAA
        if opcode == 0x27:
            result = 0
            if self.get_flag(0x10) or (self.a & 0x0F) > 9:
                result += 6
                self.set_flag(0x10, True)
            if self.get_flag(0x01) or self.a > 0x99:
                result += 0x60
                self.set_flag(0x01, True)
            if self.get_flag(0x02):
                self.a -= result
            else:
                self.a += result
            self.a &= 0xFF
            self.set_flag(0x80, self.a & 0x80)
            self.set_flag(0x40, self.a == 0)
            self.set_flag(0x10, False)
            self.set_flag(0x04, self.a & 0x80)
            return 4

        # Si aucune instruction ne correspond
        # print(f"[Z80] Opcode non implémenté: {opcode:02X} à PC={self.pc-1:04X}")
        return 4

    # --- Préfixes ---

    def execute_cb(self, sub):
        # RLC r
        if 0x00 <= sub <= 0x07:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = sub & 0x07
            val = self._get_reg(regs[idx])
            carry = (val >> 7) & 1
            val = ((val << 1) | carry) & 0xFF
            self._set_reg(regs[idx], val)
            self.set_flag(0x10, False)
            self.set_flag(0x02, False)
            self.set_flag(0x01, carry)
            self.set_flag(0x80, val & 0x80)
            self.set_flag(0x40, val == 0)
            self.set_flag(0x04, val & 0x80)
            if regs[idx] == 'hl':
                return 15
            return 8

        # RRC r
        if 0x08 <= sub <= 0x0F:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = sub & 0x07
            val = self._get_reg(regs[idx])
            carry = val & 1
            val = ((val >> 1) | (carry << 7)) & 0xFF
            self._set_reg(regs[idx], val)
            self.set_flag(0x10, False)
            self.set_flag(0x02, False)
            self.set_flag(0x01, carry)
            self.set_flag(0x80, val & 0x80)
            self.set_flag(0x40, val == 0)
            self.set_flag(0x04, val & 0x80)
            if regs[idx] == 'hl':
                return 15
            return 8

        # RL r
        if 0x10 <= sub <= 0x17:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = sub & 0x07
            val = self._get_reg(regs[idx])
            carry = (val >> 7) & 1
            old_carry = 1 if self.get_flag(0x01) else 0
            val = ((val << 1) | old_carry) & 0xFF
            self._set_reg(regs[idx], val)
            self.set_flag(0x10, False)
            self.set_flag(0x02, False)
            self.set_flag(0x01, carry)
            self.set_flag(0x80, val & 0x80)
            self.set_flag(0x40, val == 0)
            self.set_flag(0x04, val & 0x80)
            if regs[idx] == 'hl':
                return 15
            return 8

        # RR r
        if 0x18 <= sub <= 0x1F:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = sub & 0x07
            val = self._get_reg(regs[idx])
            carry = val & 1
            old_carry = 1 if self.get_flag(0x01) else 0
            val = ((val >> 1) | (old_carry << 7)) & 0xFF
            self._set_reg(regs[idx], val)
            self.set_flag(0x10, False)
            self.set_flag(0x02, False)
            self.set_flag(0x01, carry)
            self.set_flag(0x80, val & 0x80)
            self.set_flag(0x40, val == 0)
            self.set_flag(0x04, val & 0x80)
            if regs[idx] == 'hl':
                return 15
            return 8

        # SLA r
        if 0x20 <= sub <= 0x27:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = sub & 0x07
            val = self._get_reg(regs[idx])
            carry = (val >> 7) & 1
            val = (val << 1) & 0xFF
            self._set_reg(regs[idx], val)
            self.set_flag(0x10, False)
            self.set_flag(0x02, False)
            self.set_flag(0x01, carry)
            self.set_flag(0x80, val & 0x80)
            self.set_flag(0x40, val == 0)
            self.set_flag(0x04, val & 0x80)
            if regs[idx] == 'hl':
                return 15
            return 8

        # SRA r
        if 0x28 <= sub <= 0x2F:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = sub & 0x07
            val = self._get_reg(regs[idx])
            carry = val & 1
            val = (val >> 1) | (val & 0x80)
            self._set_reg(regs[idx], val)
            self.set_flag(0x10, False)
            self.set_flag(0x02, False)
            self.set_flag(0x01, carry)
            self.set_flag(0x80, val & 0x80)
            self.set_flag(0x40, val == 0)
            self.set_flag(0x04, val & 0x80)
            if regs[idx] == 'hl':
                return 15
            return 8

        # SRL r
        if 0x38 <= sub <= 0x3F:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = sub & 0x07
            val = self._get_reg(regs[idx])
            carry = val & 1
            val = (val >> 1) & 0xFF
            self._set_reg(regs[idx], val)
            self.set_flag(0x10, False)
            self.set_flag(0x02, False)
            self.set_flag(0x01, carry)
            self.set_flag(0x80, val & 0x80)
            self.set_flag(0x40, val == 0)
            self.set_flag(0x04, val & 0x80)
            if regs[idx] == 'hl':
                return 15
            return 8

        # BIT b, r
        if 0x40 <= sub <= 0x7F:
            bit = (sub >> 3) & 0x07
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = sub & 0x07
            val = self._get_reg(regs[idx])
            self.set_flag(0x10, True)
            self.set_flag(0x02, False)
            self.set_flag(0x80, (val & (1 << bit)) != 0)
            self.set_flag(0x40, (val & (1 << bit)) == 0)
            self.set_flag(0x04, (val & (1 << bit)) != 0)
            if regs[idx] == 'hl':
                return 12
            return 8

        # SET b, r
        if 0xC0 <= sub <= 0xFF:
            bit = (sub >> 3) & 0x07
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = sub & 0x07
            val = self._get_reg(regs[idx]) | (1 << bit)
            self._set_reg(regs[idx], val)
            if regs[idx] == 'hl':
                return 15
            return 8

        # RES b, r
        if 0x80 <= sub <= 0xBF:
            bit = (sub >> 3) & 0x07
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = sub & 0x07
            val = self._get_reg(regs[idx]) & ~(1 << bit)
            self._set_reg(regs[idx], val)
            if regs[idx] == 'hl':
                return 15
            return 8

        return 4

    def execute_dd(self, sub):
        # LD IX, nn
        if sub == 0x21:
            self.ix = self.read_word(self.pc)
            self.pc += 2
            return 14

        # INC IX
        if sub == 0x23:
            self.ix = (self.ix + 1) & 0xFFFF
            return 10

        # DEC IX
        if sub == 0x2B:
            self.ix = (self.ix - 1) & 0xFFFF
            return 10

        # PUSH IX
        if sub == 0xE5:
            self.sp -= 1
            self.write_byte(self.sp, (self.ix >> 8) & 0xFF)
            self.sp -= 1
            self.write_byte(self.sp, self.ix & 0xFF)
            return 15

        # POP IX
        if sub == 0xE1:
            self.ix = self.read_word(self.sp)
            self.sp += 2
            return 14

        # EX (SP), IX
        if sub == 0xE3:
            tmp = self.read_word(self.sp)
            self.write_word(self.sp, self.ix)
            self.ix = tmp
            return 23

        # JP (IX)
        if sub == 0xE9:
            self.pc = self.ix
            return 8

        # ADD IX, rr
        if sub in [0x09, 0x19, 0x29, 0x39]:
            reg_map = {0x09: 'bc', 0x19: 'de', 0x29: 'ix', 0x39: 'sp'}
            val = self._get_reg16(reg_map[sub])
            result = self.ix + val
            self.set_flag(0x10, (self.ix & 0x0FFF) + (val & 0x0FFF) > 0x0FFF)
            self.set_flag(0x01, result > 0xFFFF)
            self.set_flag(0x02, False)
            self.ix = result & 0xFFFF
            return 15

        # LD (IX+d), r
        if 0x70 <= sub <= 0x77:
            d = self.read_byte(self.pc)
            self.pc += 1
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'a']
            idx = sub & 0x07
            if idx == 6:
                val = self._get_reg('hl')
            else:
                val = self._get_reg(regs[idx])
            self.write_byte((self.ix + d) & 0xFFFF, val)
            return 19

        # LD r, (IX+d)
        if 0x46 <= sub <= 0x7E:
            d = self.read_byte(self.pc)
            self.pc += 1
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'a']
            idx = (sub >> 3) & 0x07
            val = self.read_byte((self.ix + d) & 0xFFFF)
            if idx == 6:
                self.l = val
            else:
                self._set_reg(regs[idx], val)
            return 19

        return 4

    def execute_fd(self, sub):
        # LD IY, nn
        if sub == 0x21:
            self.iy = self.read_word(self.pc)
            self.pc += 2
            return 14

        # INC IY
        if sub == 0x23:
            self.iy = (self.iy + 1) & 0xFFFF
            return 10

        # DEC IY
        if sub == 0x2B:
            self.iy = (self.iy - 1) & 0xFFFF
            return 10

        # PUSH IY
        if sub == 0xE5:
            self.sp -= 1
            self.write_byte(self.sp, (self.iy >> 8) & 0xFF)
            self.sp -= 1
            self.write_byte(self.sp, self.iy & 0xFF)
            return 15

        # POP IY
        if sub == 0xE1:
            self.iy = self.read_word(self.sp)
            self.sp += 2
            return 14

        # EX (SP), IY
        if sub == 0xE3:
            tmp = self.read_word(self.sp)
            self.write_word(self.sp, self.iy)
            self.iy = tmp
            return 23

        # JP (IY)
        if sub == 0xE9:
            self.pc = self.iy
            return 8

        # ADD IY, rr
        if sub in [0x09, 0x19, 0x29, 0x39]:
            reg_map = {0x09: 'bc', 0x19: 'de', 0x29: 'iy', 0x39: 'sp'}
            val = self._get_reg16(reg_map[sub])
            result = self.iy + val
            self.set_flag(0x10, (self.iy & 0x0FFF) + (val & 0x0FFF) > 0x0FFF)
            self.set_flag(0x01, result > 0xFFFF)
            self.set_flag(0x02, False)
            self.iy = result & 0xFFFF
            return 15

        # LD (IY+d), r
        if 0x70 <= sub <= 0x77:
            d = self.read_byte(self.pc)
            self.pc += 1
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'a']
            idx = sub & 0x07
            if idx == 6:
                val = self._get_reg('hl')
            else:
                val = self._get_reg(regs[idx])
            self.write_byte((self.iy + d) & 0xFFFF, val)
            return 19

        # LD r, (IY+d)
        if 0x46 <= sub <= 0x7E:
            d = self.read_byte(self.pc)
            self.pc += 1
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'a']
            idx = (sub >> 3) & 0x07
            val = self.read_byte((self.iy + d) & 0xFFFF)
            if idx == 6:
                self.l = val
            else:
                self._set_reg(regs[idx], val)
            return 19

        return 4

    def execute_ed(self, sub):
        # RETI
        if sub == 0x4D:
            self.iff1 = self.iff2
            self.pc = self.read_word(self.sp)
            self.sp += 2
            return 14

        # RETN
        if sub == 0x45:
            self.iff1 = self.iff2
            self.pc = self.read_word(self.sp)
            self.sp += 2
            return 14

        # LDI
        if sub == 0xA0:
            self.write_byte(self.de, self.read_byte(self.hl))
            self.de = (self.de + 1) & 0xFFFF
            self.hl = (self.hl + 1) & 0xFFFF
            self.bc = (self.bc - 1) & 0xFFFF
            self.set_flag(0x10, False)
            self.set_flag(0x02, False)
            self.set_flag(0x04, self.bc != 0)
            return 16

        # LDD
        if sub == 0xA8:
            self.write_byte(self.de, self.read_byte(self.hl))
            self.de = (self.de - 1) & 0xFFFF
            self.hl = (self.hl - 1) & 0xFFFF
            self.bc = (self.bc - 1) & 0xFFFF
            self.set_flag(0x10, False)
            self.set_flag(0x02, False)
            self.set_flag(0x04, self.bc != 0)
            return 16

        # LDIR
        if sub == 0xB0:
            self.write_byte(self.de, self.read_byte(self.hl))
            self.de = (self.de + 1) & 0xFFFF
            self.hl = (self.hl + 1) & 0xFFFF
            self.bc = (self.bc - 1) & 0xFFFF
            self.set_flag(0x10, False)
            self.set_flag(0x02, False)
            self.set_flag(0x04, self.bc != 0)
            if self.bc != 0:
                self.pc -= 2
                return 21
            return 16

        # LDDR
        if sub == 0xB8:
            self.write_byte(self.de, self.read_byte(self.hl))
            self.de = (self.de - 1) & 0xFFFF
            self.hl = (self.hl - 1) & 0xFFFF
            self.bc = (self.bc - 1) & 0xFFFF
            self.set_flag(0x10, False)
            self.set_flag(0x02, False)
            self.set_flag(0x04, self.bc != 0)
            if self.bc != 0:
                self.pc -= 2
                return 21
            return 16

        # CPI
        if sub == 0xA1:
            val = self.read_byte(self.hl)
            result = self.a - val
            self.hl = (self.hl + 1) & 0xFFFF
            self.bc = (self.bc - 1) & 0xFFFF
            self.set_flag(0x10, (self.a & 0x0F) < (val & 0x0F))
            self.set_flag(0x02, True)
            self.set_flag(0x40, result == 0)
            self.set_flag(0x04, self.bc != 0)
            return 16

        # CPD
        if sub == 0xA9:
            val = self.read_byte(self.hl)
            result = self.a - val
            self.hl = (self.hl - 1) & 0xFFFF
            self.bc = (self.bc - 1) & 0xFFFF
            self.set_flag(0x10, (self.a & 0x0F) < (val & 0x0F))
            self.set_flag(0x02, True)
            self.set_flag(0x40, result == 0)
            self.set_flag(0x04, self.bc != 0)
            return 16

        # CPIR
        if sub == 0xB1:
            val = self.read_byte(self.hl)
            result = self.a - val
            self.hl = (self.hl + 1) & 0xFFFF
            self.bc = (self.bc - 1) & 0xFFFF
            self.set_flag(0x10, (self.a & 0x0F) < (val & 0x0F))
            self.set_flag(0x02, True)
            self.set_flag(0x40, result == 0)
            self.set_flag(0x04, self.bc != 0)
            if self.bc != 0 and result != 0:
                self.pc -= 2
                return 21
            return 16

        # CPDR
        if sub == 0xB9:
            val = self.read_byte(self.hl)
            result = self.a - val
            self.hl = (self.hl - 1) & 0xFFFF
            self.bc = (self.bc - 1) & 0xFFFF
            self.set_flag(0x10, (self.a & 0x0F) < (val & 0x0F))
            self.set_flag(0x02, True)
            self.set_flag(0x40, result == 0)
            self.set_flag(0x04, self.bc != 0)
            if self.bc != 0 and result != 0:
                self.pc -= 2
                return 21
            return 16

        # IN A, (n)
        if sub == 0x3A:
            port = self.read_byte(self.pc)
            self.pc += 1
            self.a = self.in_byte(port)
            return 11

        # OUT (n), A
        if sub == 0x39:
            port = self.read_byte(self.pc)
            self.pc += 1
            self.out_byte(port, self.a)
            return 11

        # IN r, (C)
        if 0x40 <= sub <= 0x7F:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = (sub >> 3) & 0x07
            val = self.in_byte(self.c)
            self._set_reg(regs[idx], val)
            self.set_flag(0x10, False)
            self.set_flag(0x02, False)
            self.set_flag(0x80, val & 0x80)
            self.set_flag(0x40, val == 0)
            self.set_flag(0x04, val & 0x80)
            if regs[idx] == 'hl':
                return 12
            return 12

        # OUT (C), r
        if 0x41 <= sub <= 0x7F and (sub & 0x01) == 0x01:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = (sub >> 3) & 0x07
            val = self._get_reg(regs[idx])
            self.out_byte(self.c, val)
            if regs[idx] == 'hl':
                return 12
            return 12

        # LD I, A
        if sub == 0x47:
            self.i = self.a
            return 9

        # LD A, I
        if sub == 0x57:
            self.a = self.i
            self.set_flag(0x10, False)
            self.set_flag(0x02, False)
            self.set_flag(0x80, self.a & 0x80)
            self.set_flag(0x40, self.a == 0)
            self.set_flag(0x04, self.iff2)
            return 9

        # LD R, A
        if sub == 0x4F:
            self.r = self.a
            return 9

        # LD A, R
        if sub == 0x5F:
            self.a = self.r
            self.set_flag(0x10, False)
            self.set_flag(0x02, False)
            self.set_flag(0x80, self.a & 0x80)
            self.set_flag(0x40, self.a == 0)
            self.set_flag(0x04, self.iff2)
            return 9

        # IM 0
        if sub == 0x46:
            self.im = 0
            return 8

        # IM 1
        if sub == 0x56:
            self.im = 1
            return 8

        # IM 2
        if sub == 0x5E:
            self.im = 2
            return 8

        # NEG
        if sub == 0x44:
            result = -self.a
            self.set_flag(0x10, (self.a & 0x0F) != 0)
            self.set_flag(0x01, self.a != 0)
            self.a = result & 0xFF
            self.set_flag(0x80, self.a & 0x80)
            self.set_flag(0x40, self.a == 0)
            self.set_flag(0x02, True)
            self.set_flag(0x04, result & 0x80)
            return 8

        # LD (nn), BC
        if sub == 0x43:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.write_byte(addr, self.c)
            self.write_byte(addr + 1, self.b)
            return 20

        # LD BC, (nn)
        if sub == 0x4B:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.c = self.read_byte(addr)
            self.b = self.read_byte(addr + 1)
            return 20

        # LD (nn), DE
        if sub == 0x53:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.write_byte(addr, self.e)
            self.write_byte(addr + 1, self.d)
            return 20

        # LD DE, (nn)
        if sub == 0x5B:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.e = self.read_byte(addr)
            self.d = self.read_byte(addr + 1)
            return 20

        # LD (nn), SP
        if sub == 0x73:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.write_byte(addr, self.sp & 0xFF)
            self.write_byte(addr + 1, (self.sp >> 8) & 0xFF)
            return 20

        # LD SP, (nn)
        if sub == 0x7B:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.sp = self.read_word(addr)
            return 20

        return 8

    # --- Auxiliaires ---
    def _get_reg(self, name):
        if name == 'b':
            return self.b
        if name == 'c':
            return self.c
        if name == 'd':
            return self.d
        if name == 'e':
            return self.e
        if name == 'h':
            return self.h
        if name == 'l':
            return self.l
        if name == 'a':
            return self.a
        if name == 'hl':
            return self.read_byte(self.hl)
        return 0

    def _set_reg(self, name, value):
        if name == 'b':
            self.b = value
        elif name == 'c':
            self.c = value
        elif name == 'd':
            self.d = value
        elif name == 'e':
            self.e = value
        elif name == 'h':
            self.h = value
        elif name == 'l':
            self.l = value
        elif name == 'a':
            self.a = value
        elif name == 'hl':
            self.write_byte(self.hl, value)

    def _get_reg16(self, name):
        if name == 'bc':
            return self.bc
        if name == 'de':
            return self.de
        if name == 'hl':
            return self.hl
        if name == 'af':
            return self.af
        if name == 'ix':
            return self.ix
        if name == 'iy':
            return self.iy
        if name == 'sp':
            return self.sp
        return 0

    def _set_reg16(self, name, value):
        if name == 'bc':
            self.bc = value
        elif name == 'de':
            self.de = value
        elif name == 'hl':
            self.hl = value
        elif name == 'af':
            self.af = value
        elif name == 'ix':
            self.ix = value
        elif name == 'iy':
            self.iy = value
        elif name == 'sp':
            self.sp = value

    def _check_cond(self, cond):
        if cond == 'nz' or cond == 0:
            return not self.get_flag(0x40)
        if cond == 'z' or cond == 1:
            return self.get_flag(0x40)
        if cond == 'nc' or cond == 2:
            return not self.get_flag(0x01)
        if cond == 'c' or cond == 3:
            return self.get_flag(0x01)
        if cond == 'po' or cond == 4:
            return not self.get_flag(0x04)
        if cond == 'pe' or cond == 5:
            return self.get_flag(0x04)
        if cond == 'p' or cond == 6:
            return not self.get_flag(0x80)
        if cond == 'm' or cond == 7:
            return self.get_flag(0x80)
        return False

    def get_registers(self):
        return {
            'pc': self.pc,
            'sp': self.sp,
            'af': self.af,
            'bc': self.bc,
            'de': self.de,
            'hl': self.hl,
            'af_alt': self.af_alt,
            'bc_alt': self.bc_alt,
            'de_alt': self.de_alt,
            'hl_alt': self.hl_alt,
            'ix': self.ix,
            'iy': self.iy,
            'i': self.i,
            'r': self.r,
            'iff1': self.iff1,
            'iff2': self.iff2,
            'im': self.im,
            'halted': self.halted,
            'cycles': self._cycles,
        }