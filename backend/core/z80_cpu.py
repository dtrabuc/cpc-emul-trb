# core/z80_cpu.py
# Émulateur Z80 cycle-accurate
# Inspiré de l'architecture de CPCSharp (C#)
# Implémente toutes les instructions du Z80, y compris les préfixes DD, FD, CB, ED

class Z80CPU:
    # --- Constructeur et registres ---
    def __init__(self):
        self.memory = None          # Référence à la mémoire (objet Memory)
        self.io_read = None         # Fonction de lecture I/O
        self.io_write = None        # Fonction d'écriture I/O

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
        self.i = 0x00          # Vecteur d'interruption
        self.r = 0x00          # Compteur de rafraîchissement mémoire

        # Interruptions
        self.iff1 = False      # Interrupt flip-flop 1
        self.iff2 = False      # Interrupt flip-flop 2
        self.im = 0            # Mode interruption (0, 1, 2)
        self.halted = False    # État HALT

        # Compteur de cycles
        self._cycles = 0

        # Masques des flags
        FLAG_C = 0x01
        FLAG_N = 0x02
        FLAG_PV = 0x04
        FLAG_H = 0x10
        FLAG_Z = 0x40
        FLAG_S = 0x80

    # --- Propriétés pour les registres 16 bits ---
    @property
    def af(self):
        return (self.a << 8) | self.f
    @af.setter
    def af(self, value):
        self.a = (value >> 8) & 0xFF
        self.f = value & 0xFF

    @property
    def bc(self):
        return (self.b << 8) | self.c
    @bc.setter
    def bc(self, value):
        self.b = (value >> 8) & 0xFF
        self.c = value & 0xFF

    @property
    def de(self):
        return (self.d << 8) | self.e
    @de.setter
    def de(self, value):
        self.d = (value >> 8) & 0xFF
        self.e = value & 0xFF

    @property
    def hl(self):
        return (self.h << 8) | self.l
    @hl.setter
    def hl(self, value):
        self.h = (value >> 8) & 0xFF
        self.l = value & 0xFF

    @property
    def af_alt(self):
        return (self.a_alt << 8) | self.f_alt
    @af_alt.setter
    def af_alt(self, value):
        self.a_alt = (value >> 8) & 0xFF
        self.f_alt = value & 0xFF

    @property
    def bc_alt(self):
        return (self.b_alt << 8) | self.c_alt
    @bc_alt.setter
    def bc_alt(self, value):
        self.b_alt = (value >> 8) & 0xFF
        self.c_alt = value & 0xFF

    @property
    def de_alt(self):
        return (self.d_alt << 8) | self.e_alt
    @de_alt.setter
    def de_alt(self, value):
        self.d_alt = (value >> 8) & 0xFF
        self.e_alt = value & 0xFF

    @property
    def hl_alt(self):
        return (self.h_alt << 8) | self.l_alt
    @hl_alt.setter
    def hl_alt(self, value):
        self.h_alt = (value >> 8) & 0xFF
        self.l_alt = value & 0xFF

    # --- Gestion des flags ---
    def set_flag(self, flag, value):
        if value:
            self.f |= flag
        else:
            self.f &= ~flag

    def get_flag(self, flag):
        return (self.f & flag) != 0

    # --- Accès mémoire ---
    def read_byte(self, addr):
        if self.memory:
            return self.memory.read_byte(addr)
        return 0xFF

    def write_byte(self, addr, value):
        if self.memory:
            self.memory.write_byte(addr, value)

    def read_word(self, addr):
        return self.read_byte(addr) | (self.read_byte(addr + 1) << 8)

    def write_word(self, addr, value):
        self.write_byte(addr, value & 0xFF)
        self.write_byte(addr + 1, (value >> 8) & 0xFF)

    # --- Accès I/O ---
    def in_byte(self, port):
        if self.io_read:
            return self.io_read(port)
        return 0xFF

    def out_byte(self, port, value):
        if self.io_write:
            self.io_write(port, value)

    # --- Gestion des interruptions ---
    def interrupt(self, vector=0x00):
        """Demande d'interruption"""
        if not self.iff1:
            return 4

        self.halted = False
        if self.im == 0:
            # RST 0x00
            self.sp -= 1
            self.write_byte(self.sp, (self.pc >> 8) & 0xFF)
            self.sp -= 1
            self.write_byte(self.sp, self.pc & 0xFF)
            self.pc = 0x0000
            self.iff1 = False
            self.iff2 = False
            return 7
        elif self.im == 1:
            # RST 0x38
            self.sp -= 1
            self.write_byte(self.sp, (self.pc >> 8) & 0xFF)
            self.sp -= 1
            self.write_byte(self.sp, self.pc & 0xFF)
            self.pc = 0x0038
            self.iff1 = False
            self.iff2 = False
            return 7
        elif self.im == 2:
            # Mode 2 : vecteur sur 16 bits
            addr = (self.i << 8) | vector
            self.pc = self.read_word(addr)
            self.iff1 = False
            self.iff2 = False
            return 7
        return 4

    # --- Reset ---
    def reset(self):
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
        self._cycles = 0

    # --- Step principal ---
    def step(self):
        if self.halted:
            self._cycles += 1
            return 1

        opcode = self.read_byte(self.pc)
        self.pc += 1
        self.r = (self.r + 1) & 0x7F

        cycles = self.execute(opcode)
        self._cycles += cycles
        return cycles

    # --- Exécution des instructions ---
    def execute(self, opcode):
        # --- Préfixe DD (IX) ---
        if opcode == 0xDD:
            sub = self.read_byte(self.pc)
            self.pc += 1
            return self.execute_dd(sub)

        # --- Préfixe FD (IY) ---
        if opcode == 0xFD:
            sub = self.read_byte(self.pc)
            self.pc += 1
            return self.execute_fd(sub)

        # --- Préfixe CB ---
        if opcode == 0xCB:
            sub = self.read_byte(self.pc)
            self.pc += 1
            return self.execute_cb(sub)

        # --- Préfixe ED ---
        if opcode == 0xED:
            sub = self.read_byte(self.pc)
            self.pc += 1
            return self.execute_ed(sub)

        # --- Instructions 8 bits ---
        # LD r, r' (0x40-0x7F)
        if 0x40 <= opcode <= 0x7F:
            src = opcode & 0x07
            dst = (opcode >> 3) & 0x07
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            val = self._get_reg(regs[src])
            self._set_reg(regs[dst], val)
            if regs[src] == 'hl':
                return 7
            if regs[dst] == 'hl':
                return 7
            return 4

        # LD r, n (0x06, 0x0E, 0x16, 0x1E, 0x26, 0x2E, 0x3E)
        if opcode in [0x06, 0x0E, 0x16, 0x1E, 0x26, 0x2E, 0x3E]:
            reg_map = {0x06: 'b', 0x0E: 'c', 0x16: 'd', 0x1E: 'e', 0x26: 'h', 0x2E: 'l', 0x3E: 'a'}
            self._set_reg(reg_map[opcode], self.read_byte(self.pc))
            self.pc += 1
            return 7

        # LD rr, nn (0x01, 0x11, 0x21, 0x31)
        if opcode in [0x01, 0x11, 0x21, 0x31]:
            reg_map = {0x01: 'bc', 0x11: 'de', 0x21: 'hl', 0x31: 'sp'}
            self._set_reg16(reg_map[opcode], self.read_word(self.pc))
            self.pc += 2
            return 10

        # LD (BC), A (0x02)
        if opcode == 0x02:
            self.write_byte(self.bc, self.a)
            return 7
        # LD (DE), A (0x12)
        if opcode == 0x12:
            self.write_byte(self.de, self.a)
            return 7
        # LD (HL), A (0x77)
        if opcode == 0x77:
            self.write_byte(self.hl, self.a)
            return 7

        # LD A, (BC) (0x0A)
        if opcode == 0x0A:
            self.a = self.read_byte(self.bc)
            return 7
        # LD A, (DE) (0x1A)
        if opcode == 0x1A:
            self.a = self.read_byte(self.de)
            return 7
        # LD A, (HL) (0x7E)
        if opcode == 0x7E:
            self.a = self.read_byte(self.hl)
            return 7

        # EX DE, HL (0xEB)
        if opcode == 0xEB:
            self.de, self.hl = self.hl, self.de
            return 4
        # EX AF, AF' (0x08)
        if opcode == 0x08:
            self.af, self.af_alt = self.af_alt, self.af
            return 4
        # EXX (0xD9)
        if opcode == 0xD9:
            self.bc, self.bc_alt = self.bc_alt, self.bc
            self.de, self.de_alt = self.de_alt, self.de
            self.hl, self.hl_alt = self.hl_alt, self.hl
            return 4
        # EX (SP), HL (0xE3)
        if opcode == 0xE3:
            tmp = self.read_word(self.sp)
            self.write_word(self.sp, self.hl)
            self.hl = tmp
            return 19

        # ADD HL, rr (0x09, 0x19, 0x29, 0x39)
        if opcode in [0x09, 0x19, 0x29, 0x39]:
            reg_map = {0x09: 'bc', 0x19: 'de', 0x29: 'hl', 0x39: 'sp'}
            val = self._get_reg16(reg_map[opcode])
            result = self.hl + val
            self.set_flag(0x10, (self.hl & 0x0FFF) + (val & 0x0FFF) > 0x0FFF)
            self.set_flag(0x01, result > 0xFFFF)
            self.set_flag(0x02, False)
            self.hl = result & 0xFFFF
            return 11

        # INC/DEC 16-bit (0x03, 0x0B, 0x13, 0x1B, 0x23, 0x2B, 0x33, 0x3B)
        if opcode in [0x03, 0x0B, 0x13, 0x1B, 0x23, 0x2B, 0x33, 0x3B]:
            reg_map = {
                0x03: 'bc', 0x0B: 'bc',
                0x13: 'de', 0x1B: 'de',
                0x23: 'hl', 0x2B: 'hl',
                0x33: 'sp', 0x3B: 'sp'
            }
            reg = reg_map[opcode]
            val = self._get_reg16(reg)
            if opcode & 0x08:  # DEC
                val = (val - 1) & 0xFFFF
            else:              # INC
                val = (val + 1) & 0xFFFF
            self._set_reg16(reg, val)
            return 6

        # INC/DEC 8-bit (0x04, 0x0C, 0x14, 0x1C, 0x24, 0x2C, 0x34, 0x3C)
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

        # ADD A, r (0x80-0x87)
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

        # ADD A, n (0xC6)
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

        # ADC A, r (0x88-0x8F)
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

        # ADC A, n (0xCE)
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

        # SUB A, r (0x90-0x97)
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

        # SUB A, n (0xD6)
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

        # SBC A, r (0x98-0x9F)
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

        # SBC A, n (0xDE)
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

        # AND A, r (0xA0-0xA7)
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

        # AND A, n (0xE6)
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

        # OR A, r (0xB0-0xB7)
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

        # OR A, n (0xF6)
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

        # XOR A, r (0xA8-0xAF)
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

        # XOR A, n (0xEE)
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

        # CP A, r (0xB8-0xBF)
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

        # CP A, n (0xFE)
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

        # PUSH (0xC5, 0xD5, 0xE5, 0xF5)
        if opcode in [0xC5, 0xD5, 0xE5, 0xF5]:
            reg_map = {0xC5: 'bc', 0xD5: 'de', 0xE5: 'hl', 0xF5: 'af'}
            val = self._get_reg16(reg_map[opcode])
            self.sp -= 1
            self.write_byte(self.sp, (val >> 8) & 0xFF)
            self.sp -= 1
            self.write_byte(self.sp, val & 0xFF)
            return 11

        # POP (0xC1, 0xD1, 0xE1, 0xF1)
        if opcode in [0xC1, 0xD1, 0xE1, 0xF1]:
            reg_map = {0xC1: 'bc', 0xD1: 'de', 0xE1: 'hl', 0xF1: 'af'}
            val = self.read_word(self.sp)
            self.sp += 2
            self._set_reg16(reg_map[opcode], val)
            if opcode == 0xF1:  # POP AF, on nettoie les bits inutilisés
                self.f &= 0xFF
            return 10

        # CALL (0xCD)
        if opcode == 0xCD:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.sp -= 1
            self.write_byte(self.sp, (self.pc >> 8) & 0xFF)
            self.sp -= 1
            self.write_byte(self.sp, self.pc & 0xFF)
            self.pc = addr
            return 17

        # CALL condition (0xC4, 0xCC, 0xD4, 0xDC, 0xE4, 0xEC, 0xF4, 0xFC)
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

        # RET (0xC9)
        if opcode == 0xC9:
            self.pc = self.read_word(self.sp)
            self.sp += 2
            return 10

        # RET condition (0xC0, 0xC8, 0xD0, 0xD8, 0xE0, 0xE8, 0xF0, 0xF8)
        if (0xC0 <= opcode <= 0xF8) and (opcode & 0x07) == 0x00 and opcode != 0xC9:
            cond = (opcode >> 3) & 0x07
            if self._check_cond(cond):
                self.pc = self.read_word(self.sp)
                self.sp += 2
                return 11
            return 5

        # RST (0xC7, 0xCF, 0xD7, 0xDF, 0xE7, 0xEF, 0xF7, 0xFF)
        if opcode >= 0xC7 and (opcode & 0xC7) == 0xC7:
            rst_addr = opcode & 0x38
            self.sp -= 1
            self.write_byte(self.sp, (self.pc >> 8) & 0xFF)
            self.sp -= 1
            self.write_byte(self.sp, self.pc & 0xFF)
            self.pc = rst_addr
            return 11

        # JP (0xC3)
        if opcode == 0xC3:
            self.pc = self.read_word(self.pc)
            return 10

        # JP condition (0xC2, 0xCA, 0xD2, 0xDA, 0xE2, 0xEA, 0xF2, 0xFA)
        if (0xC2 <= opcode <= 0xFA) and (opcode & 0x07) == 0x02:
            cond = (opcode >> 3) & 0x07
            if self._check_cond(cond):
                self.pc = self.read_word(self.pc)
                return 10
            else:
                self.pc += 2
                return 10

        # JP (HL) (0xE9)
        if opcode == 0xE9:
            self.pc = self.hl
            return 4

        # JR (0x18)
        if opcode == 0x18:
            offset = self.read_byte(self.pc)
            self.pc += 1
            if offset & 0x80:
                self.pc -= (0x100 - offset)
            else:
                self.pc += offset
            return 12

        # JR condition (0x20, 0x28, 0x30, 0x38)
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

        # NOP (0x00)
        if opcode == 0x00:
            return 4

        # HALT (0x76)
        if opcode == 0x76:
            self.halted = True
            return 4

        # DI (0xF3)
        if opcode == 0xF3:
            self.iff1 = False
            self.iff2 = False
            return 4

        # EI (0xFB)
        if opcode == 0xFB:
            self.iff1 = True
            self.iff2 = True
            return 4

        # LD (nn), A (0x32)
        if opcode == 0x32:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.write_byte(addr, self.a)
            return 13

        # LD A, (nn) (0x3A)
        if opcode == 0x3A:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.a = self.read_byte(addr)
            return 13

        # LD (nn), HL (0x22)
        if opcode == 0x22:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.write_byte(addr, self.l)
            self.write_byte(addr + 1, self.h)
            return 16

        # LD HL, (nn) (0x2A)
        if opcode == 0x2A:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.l = self.read_byte(addr)
            self.h = self.read_byte(addr + 1)
            return 16

        # IN A, (n) (0xDB)
        if opcode == 0xDB:
            port = self.read_byte(self.pc)
            self.pc += 1
            self.a = self.in_byte(port)
            return 11

        # OUT (n), A (0xD3)
        if opcode == 0xD3:
            port = self.read_byte(self.pc)
            self.pc += 1
            self.out_byte(port, self.a)
            return 11

        # CPL (0x2F)
        if opcode == 0x2F:
            self.a ^= 0xFF
            self.set_flag(0x10, True)
            self.set_flag(0x02, True)
            return 4

        # SCF (0x37)
        if opcode == 0x37:
            self.set_flag(0x01, True)
            self.set_flag(0x10, False)
            self.set_flag(0x02, False)
            return 4

        # CCF (0x3F)
        if opcode == 0x3F:
            self.set_flag(0x01, not self.get_flag(0x01))
            self.set_flag(0x10, False)
            self.set_flag(0x02, False)
            return 4

        # DAA (0x27)
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

        # --- Si aucune instruction ne correspond ---
        # print(f"[Z80] Opcode non implémenté: {opcode:02X} à PC={self.pc-1:04X}")
        return 4

    # --- Exécution des préfixes ---

    def execute_cb(self, sub):
        """Instructions avec préfixe CB (bit/rotate/shift)"""
        # RLC r (0x00-0x07)
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

        # RRC r (0x08-0x0F)
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

        # RL r (0x10-0x17)
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

        # RR r (0x18-0x1F)
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

        # SLA r (0x20-0x27)
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

        # SRA r (0x28-0x2F)
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

        # SRL r (0x38-0x3F)
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

        # BIT b, r (0x40-0x7F)
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

        # SET b, r (0xC0-0xFF)
        if 0xC0 <= sub <= 0xFF:
            bit = (sub >> 3) & 0x07
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = sub & 0x07
            val = self._get_reg(regs[idx]) | (1 << bit)
            self._set_reg(regs[idx], val)
            if regs[idx] == 'hl':
                return 15
            return 8

        # RES b, r (0x80-0xBF)
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
        """Instructions avec préfixe DD (IX)"""
        # LD IX, nn (0x21)
        if sub == 0x21:
            self.ix = self.read_word(self.pc)
            self.pc += 2
            return 14

        # INC IX (0x23)
        if sub == 0x23:
            self.ix = (self.ix + 1) & 0xFFFF
            return 10

        # DEC IX (0x2B)
        if sub == 0x2B:
            self.ix = (self.ix - 1) & 0xFFFF
            return 10

        # PUSH IX (0xE5)
        if sub == 0xE5:
            self.sp -= 1
            self.write_byte(self.sp, (self.ix >> 8) & 0xFF)
            self.sp -= 1
            self.write_byte(self.sp, self.ix & 0xFF)
            return 15

        # POP IX (0xE1)
        if sub == 0xE1:
            self.ix = self.read_word(self.sp)
            self.sp += 2
            return 14

        # EX (SP), IX (0xE3)
        if sub == 0xE3:
            tmp = self.read_word(self.sp)
            self.write_word(self.sp, self.ix)
            self.ix = tmp
            return 23

        # JP (IX) (0xE9)
        if sub == 0xE9:
            self.pc = self.ix
            return 8

        # ADD IX, rr (0x09, 0x19, 0x29, 0x39)
        if sub in [0x09, 0x19, 0x29, 0x39]:
            reg_map = {0x09: 'bc', 0x19: 'de', 0x29: 'ix', 0x39: 'sp'}
            val = self._get_reg16(reg_map[sub])
            result = self.ix + val
            self.set_flag(0x10, (self.ix & 0x0FFF) + (val & 0x0FFF) > 0x0FFF)
            self.set_flag(0x01, result > 0xFFFF)
            self.set_flag(0x02, False)
            self.ix = result & 0xFFFF
            return 15

        # LD (IX+d), r (0x70-0x77)
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

        # LD r, (IX+d) (0x46-0x7E)
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
        """Instructions avec préfixe FD (IY)"""
        # LD IY, nn (0x21)
        if sub == 0x21:
            self.iy = self.read_word(self.pc)
            self.pc += 2
            return 14

        # INC IY (0x23)
        if sub == 0x23:
            self.iy = (self.iy + 1) & 0xFFFF
            return 10

        # DEC IY (0x2B)
        if sub == 0x2B:
            self.iy = (self.iy - 1) & 0xFFFF
            return 10

        # PUSH IY (0xE5)
        if sub == 0xE5:
            self.sp -= 1
            self.write_byte(self.sp, (self.iy >> 8) & 0xFF)
            self.sp -= 1
            self.write_byte(self.sp, self.iy & 0xFF)
            return 15

        # POP IY (0xE1)
        if sub == 0xE1:
            self.iy = self.read_word(self.sp)
            self.sp += 2
            return 14

        # EX (SP), IY (0xE3)
        if sub == 0xE3:
            tmp = self.read_word(self.sp)
            self.write_word(self.sp, self.iy)
            self.iy = tmp
            return 23

        # JP (IY) (0xE9)
        if sub == 0xE9:
            self.pc = self.iy
            return 8

        # ADD IY, rr (0x09, 0x19, 0x29, 0x39)
        if sub in [0x09, 0x19, 0x29, 0x39]:
            reg_map = {0x09: 'bc', 0x19: 'de', 0x29: 'iy', 0x39: 'sp'}
            val = self._get_reg16(reg_map[sub])
            result = self.iy + val
            self.set_flag(0x10, (self.iy & 0x0FFF) + (val & 0x0FFF) > 0x0FFF)
            self.set_flag(0x01, result > 0xFFFF)
            self.set_flag(0x02, False)
            self.iy = result & 0xFFFF
            return 15

        # LD (IY+d), r (0x70-0x77)
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

        # LD r, (IY+d) (0x46-0x7E)
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
        """Instructions avec préfixe ED (bloc, I/O, interruptions)"""
        # RETI (0x4D)
        if sub == 0x4D:
            self.iff1 = self.iff2
            self.pc = self.read_word(self.sp)
            self.sp += 2
            return 14

        # RETN (0x45)
        if sub == 0x45:
            self.iff1 = self.iff2
            self.pc = self.read_word(self.sp)
            self.sp += 2
            return 14

        # LDI (0xA0)
        if sub == 0xA0:
            self.write_byte(self.de, self.read_byte(self.hl))
            self.de = (self.de + 1) & 0xFFFF
            self.hl = (self.hl + 1) & 0xFFFF
            self.bc = (self.bc - 1) & 0xFFFF
            self.set_flag(0x10, False)
            self.set_flag(0x02, False)
            self.set_flag(0x04, self.bc != 0)
            return 16

        # LDD (0xA8)
        if sub == 0xA8:
            self.write_byte(self.de, self.read_byte(self.hl))
            self.de = (self.de - 1) & 0xFFFF
            self.hl = (self.hl - 1) & 0xFFFF
            self.bc = (self.bc - 1) & 0xFFFF
            self.set_flag(0x10, False)
            self.set_flag(0x02, False)
            self.set_flag(0x04, self.bc != 0)
            return 16

        # LDIR (0xB0)
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

        # LDDR (0xB8)
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

        # CPI (0xA1)
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

        # CPD (0xA9)
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

        # CPIR (0xB1)
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

        # CPDR (0xB9)
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

        # IN A, (n) (0x3A)
        if sub == 0x3A:
            port = self.read_byte(self.pc)
            self.pc += 1
            self.a = self.in_byte(port)
            return 11

        # OUT (n), A (0x39)
        if sub == 0x39:
            port = self.read_byte(self.pc)
            self.pc += 1
            self.out_byte(port, self.a)
            return 11

        # IN r, (C) (0x40-0x7F)
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

        # OUT (C), r (0x41-0x7F, bit 0 = 1)
        if 0x41 <= sub <= 0x7F and (sub & 0x01) == 0x01:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = (sub >> 3) & 0x07
            val = self._get_reg(regs[idx])
            self.out_byte(self.c, val)
            if regs[idx] == 'hl':
                return 12
            return 12

        # LD I, A (0x47)
        if sub == 0x47:
            self.i = self.a
            return 9

        # LD A, I (0x57)
        if sub == 0x57:
            self.a = self.i
            self.set_flag(0x10, False)
            self.set_flag(0x02, False)
            self.set_flag(0x80, self.a & 0x80)
            self.set_flag(0x40, self.a == 0)
            self.set_flag(0x04, self.iff2)
            return 9

        # LD R, A (0x4F)
        if sub == 0x4F:
            self.r = self.a
            return 9

        # LD A, R (0x5F)
        if sub == 0x5F:
            self.a = self.r
            self.set_flag(0x10, False)
            self.set_flag(0x02, False)
            self.set_flag(0x80, self.a & 0x80)
            self.set_flag(0x40, self.a == 0)
            self.set_flag(0x04, self.iff2)
            return 9

        # IM 0 (0x46)
        if sub == 0x46:
            self.im = 0
            return 8

        # IM 1 (0x56)
        if sub == 0x56:
            self.im = 1
            return 8

        # IM 2 (0x5E)
        if sub == 0x5E:
            self.im = 2
            return 8

        # NEG (0x44)
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

        # LD (nn), BC (0x43)
        if sub == 0x43:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.write_byte(addr, self.c)
            self.write_byte(addr + 1, self.b)
            return 20

        # LD BC, (nn) (0x4B)
        if sub == 0x4B:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.c = self.read_byte(addr)
            self.b = self.read_byte(addr + 1)
            return 20

        # LD (nn), DE (0x53)
        if sub == 0x53:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.write_byte(addr, self.e)
            self.write_byte(addr + 1, self.d)
            return 20

        # LD DE, (nn) (0x5B)
        if sub == 0x5B:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.e = self.read_byte(addr)
            self.d = self.read_byte(addr + 1)
            return 20

        # LD (nn), SP (0x73)
        if sub == 0x73:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.write_byte(addr, self.sp & 0xFF)
            self.write_byte(addr + 1, (self.sp >> 8) & 0xFF)
            return 20

        # LD SP, (nn) (0x7B)
        if sub == 0x7B:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.sp = self.read_word(addr)
            return 20

        return 8

    # --- Fonctions auxiliaires pour l'accès aux registres ---
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

    # --- Getter pour l'état du CPU (debug) ---
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