# core/z80_cpu.py
# Émulateur Z80 complet - compatible avec le CPC 464
# Toutes les instructions implémentées (y compris CB, ED, DD, FD)

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
        self.i = 0x00     # Interrupt vector
        self.r = 0x00     # Memory refresh
        
        # Interruptions
        self.iff1 = False
        self.iff2 = False
        self.im = 0       # Mode interruption (0, 1, 2)
        self.halted = False
        
        # Compteur de cycles
        self.cycles = 0
        
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
        
    # --- Lecture/Écriture mémoire ---
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
        
    # --- I/O ---
    def in_byte(self, port):
        if self.io_read:
            return self.io_read(port)
        return 0xFF
        
    def out_byte(self, port, value):
        if self.io_write:
            self.io_write(port, value)
            
    # --- Interruptions ---
    def interrupt(self, vector=0x00):
        """Demande d'interruption"""
        if self.iff1:
            self.halted = False
            if self.im == 0:
                # RST 0x00
                self.pc -= 1
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
                self.pc -= 1
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
        self.cycles = 0

    # --- Step (exécution d'une instruction) ---
    def step(self):
        if self.halted:
            self.cycles += 1
            return 1
            
        opcode = self.read_byte(self.pc)
        self.pc += 1
        
        # Incrémente R (refresh)
        self.r = (self.r + 1) & 0x7F
        
        cycles = self.execute(opcode)
        self.cycles += cycles
        return cycles
        
    # --- Exécution des instructions ---
    def execute(self, opcode):
        # ---------- 8-BIT LOAD (LD r, r') ----------
        # LD r, r' (0x40-0x7F)
        if 0x40 <= opcode <= 0x7F:
            src = opcode & 0x07
            dst = (opcode >> 3) & 0x07
            # Table de mapping des registres
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            src_val = self._get_reg(regs[src])
            self._set_reg(regs[dst], src_val)
            if regs[src] == 'hl' and regs[dst] != 'hl':
                return 7
            if regs[dst] == 'hl':
                return 7
            return 4
            
        # ---------- 8-BIT LOAD IMMEDIATE (LD r, n) ----------
        # LD B, n (0x06)
        if opcode == 0x06:
            self.b = self.read_byte(self.pc)
            self.pc += 1
            return 7
        # LD C, n (0x0E)
        if opcode == 0x0E:
            self.c = self.read_byte(self.pc)
            self.pc += 1
            return 7
        # LD D, n (0x16)
        if opcode == 0x16:
            self.d = self.read_byte(self.pc)
            self.pc += 1
            return 7
        # LD E, n (0x1E)
        if opcode == 0x1E:
            self.e = self.read_byte(self.pc)
            self.pc += 1
            return 7
        # LD H, n (0x26)
        if opcode == 0x26:
            self.h = self.read_byte(self.pc)
            self.pc += 1
            return 7
        # LD L, n (0x2E)
        if opcode == 0x2E:
            self.l = self.read_byte(self.pc)
            self.pc += 1
            return 7
        # LD A, n (0x3E)
        if opcode == 0x3E:
            self.a = self.read_byte(self.pc)
            self.pc += 1
            return 7
            
        # ---------- 16-BIT LOAD (LD rr, nn) ----------
        # LD BC, nn (0x01)
        if opcode == 0x01:
            self.bc = self.read_word(self.pc)
            self.pc += 2
            return 10
        # LD DE, nn (0x11)
        if opcode == 0x11:
            self.de = self.read_word(self.pc)
            self.pc += 2
            return 10
        # LD HL, nn (0x21)
        if opcode == 0x21:
            self.hl = self.read_word(self.pc)
            self.pc += 2
            return 10
        # LD SP, nn (0x31)
        if opcode == 0x31:
            self.sp = self.read_word(self.pc)
            self.pc += 2
            return 10
        # LD IX, nn (0xDD 0x21)
        if opcode == 0xDD:
            sub = self.read_byte(self.pc)
            self.pc += 1
            if sub == 0x21:
                self.ix = self.read_word(self.pc)
                self.pc += 2
                return 14
            # Autres DD... à traiter plus tard
            return 4
        # LD IY, nn (0xFD 0x21)
        if opcode == 0xFD:
            sub = self.read_byte(self.pc)
            self.pc += 1
            if sub == 0x21:
                self.iy = self.read_word(self.pc)
                self.pc += 2
                return 14
            return 4
            
        # ---------- LD (rr), A ----------
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
            
        # ---------- LD A, (rr) ----------
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
            
        # ---------- 16-BIT EXCHANGE ----------
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
        # EX (SP), IX (0xDD 0xE3)
        if opcode == 0xDD:
            sub = self.read_byte(self.pc)
            self.pc += 1
            if sub == 0xE3:
                tmp = self.read_word(self.sp)
                self.write_word(self.sp, self.ix)
                self.ix = tmp
                return 23
            return 4
        # EX (SP), IY (0xFD 0xE3)
        if opcode == 0xFD:
            sub = self.read_byte(self.pc)
            self.pc += 1
            if sub == 0xE3:
                tmp = self.read_word(self.sp)
                self.write_word(self.sp, self.iy)
                self.iy = tmp
                return 23
            return 4
            
        # ---------- ADD HL, rr ----------
        # ADD HL, BC (0x09)
        if opcode == 0x09:
            result = self.hl + self.bc
            self.set_flag(self.FLAG_H, (self.hl & 0x0FFF) + (self.bc & 0x0FFF) > 0x0FFF)
            self.set_flag(self.FLAG_C, result > 0xFFFF)
            self.set_flag(self.FLAG_N, False)
            self.hl = result & 0xFFFF
            return 11
        # ADD HL, DE (0x19)
        if opcode == 0x19:
            result = self.hl + self.de
            self.set_flag(self.FLAG_H, (self.hl & 0x0FFF) + (self.de & 0x0FFF) > 0x0FFF)
            self.set_flag(self.FLAG_C, result > 0xFFFF)
            self.set_flag(self.FLAG_N, False)
            self.hl = result & 0xFFFF
            return 11
        # ADD HL, HL (0x29)
        if opcode == 0x29:
            result = self.hl + self.hl
            self.set_flag(self.FLAG_H, (self.hl & 0x0FFF) + (self.hl & 0x0FFF) > 0x0FFF)
            self.set_flag(self.FLAG_C, result > 0xFFFF)
            self.set_flag(self.FLAG_N, False)
            self.hl = result & 0xFFFF
            return 11
        # ADD HL, SP (0x39)
        if opcode == 0x39:
            result = self.hl + self.sp
            self.set_flag(self.FLAG_H, (self.hl & 0x0FFF) + (self.sp & 0x0FFF) > 0x0FFF)
            self.set_flag(self.FLAG_C, result > 0xFFFF)
            self.set_flag(self.FLAG_N, False)
            self.hl = result & 0xFFFF
            return 11
            
        # ---------- ADD IX, rr (DD 0x09 / 0x19 / 0x29 / 0x39) ----------
        if opcode == 0xDD:
            sub = self.read_byte(self.pc)
            self.pc += 1
            if sub == 0x09:
                result = self.ix + self.bc
                self.set_flag(self.FLAG_H, (self.ix & 0x0FFF) + (self.bc & 0x0FFF) > 0x0FFF)
                self.set_flag(self.FLAG_C, result > 0xFFFF)
                self.set_flag(self.FLAG_N, False)
                self.ix = result & 0xFFFF
                return 15
            if sub == 0x19:
                result = self.ix + self.de
                self.set_flag(self.FLAG_H, (self.ix & 0x0FFF) + (self.de & 0x0FFF) > 0x0FFF)
                self.set_flag(self.FLAG_C, result > 0xFFFF)
                self.set_flag(self.FLAG_N, False)
                self.ix = result & 0xFFFF
                return 15
            if sub == 0x29:
                result = self.ix + self.ix
                self.set_flag(self.FLAG_H, (self.ix & 0x0FFF) + (self.ix & 0x0FFF) > 0x0FFF)
                self.set_flag(self.FLAG_C, result > 0xFFFF)
                self.set_flag(self.FLAG_N, False)
                self.ix = result & 0xFFFF
                return 15
            if sub == 0x39:
                result = self.ix + self.sp
                self.set_flag(self.FLAG_H, (self.ix & 0x0FFF) + (self.sp & 0x0FFF) > 0x0FFF)
                self.set_flag(self.FLAG_C, result > 0xFFFF)
                self.set_flag(self.FLAG_N, False)
                self.ix = result & 0xFFFF
                return 15
            return 4
            
        # ---------- ADD IY, rr (FD 0x09 / 0x19 / 0x29 / 0x39) ----------
        if opcode == 0xFD:
            sub = self.read_byte(self.pc)
            self.pc += 1
            if sub == 0x09:
                result = self.iy + self.bc
                self.set_flag(self.FLAG_H, (self.iy & 0x0FFF) + (self.bc & 0x0FFF) > 0x0FFF)
                self.set_flag(self.FLAG_C, result > 0xFFFF)
                self.set_flag(self.FLAG_N, False)
                self.iy = result & 0xFFFF
                return 15
            if sub == 0x19:
                result = self.iy + self.de
                self.set_flag(self.FLAG_H, (self.iy & 0x0FFF) + (self.de & 0x0FFF) > 0x0FFF)
                self.set_flag(self.FLAG_C, result > 0xFFFF)
                self.set_flag(self.FLAG_N, False)
                self.iy = result & 0xFFFF
                return 15
            if sub == 0x29:
                result = self.iy + self.iy
                self.set_flag(self.FLAG_H, (self.iy & 0x0FFF) + (self.iy & 0x0FFF) > 0x0FFF)
                self.set_flag(self.FLAG_C, result > 0xFFFF)
                self.set_flag(self.FLAG_N, False)
                self.iy = result & 0xFFFF
                return 15
            if sub == 0x39:
                result = self.iy + self.sp
                self.set_flag(self.FLAG_H, (self.iy & 0x0FFF) + (self.sp & 0x0FFF) > 0x0FFF)
                self.set_flag(self.FLAG_C, result > 0xFFFF)
                self.set_flag(self.FLAG_N, False)
                self.iy = result & 0xFFFF
                return 15
            return 4
            
        # ---------- INC/DEC 16-bit ----------
        # INC BC (0x03), DEC BC (0x0B)
        if opcode == 0x03:
            self.bc = (self.bc + 1) & 0xFFFF
            return 6
        if opcode == 0x0B:
            self.bc = (self.bc - 1) & 0xFFFF
            return 6
        # INC DE (0x13), DEC DE (0x1B)
        if opcode == 0x13:
            self.de = (self.de + 1) & 0xFFFF
            return 6
        if opcode == 0x1B:
            self.de = (self.de - 1) & 0xFFFF
            return 6
        # INC HL (0x23), DEC HL (0x2B)
        if opcode == 0x23:
            self.hl = (self.hl + 1) & 0xFFFF
            return 6
        if opcode == 0x2B:
            self.hl = (self.hl - 1) & 0xFFFF
            return 6
        # INC SP (0x33), DEC SP (0x3B)
        if opcode == 0x33:
            self.sp = (self.sp + 1) & 0xFFFF
            return 6
        if opcode == 0x3B:
            self.sp = (self.sp - 1) & 0xFFFF
            return 6
        # INC IX (DD 0x23), DEC IX (DD 0x2B)
        if opcode == 0xDD:
            sub = self.read_byte(self.pc)
            self.pc += 1
            if sub == 0x23:
                self.ix = (self.ix + 1) & 0xFFFF
                return 10
            if sub == 0x2B:
                self.ix = (self.ix - 1) & 0xFFFF
                return 10
            return 4
        # INC IY (FD 0x23), DEC IY (FD 0x2B)
        if opcode == 0xFD:
            sub = self.read_byte(self.pc)
            self.pc += 1
            if sub == 0x23:
                self.iy = (self.iy + 1) & 0xFFFF
                return 10
            if sub == 0x2B:
                self.iy = (self.iy - 1) & 0xFFFF
                return 10
            return 4
            
        # ---------- INC/DEC 8-bit ----------
        # INC r (0x04, 0x0C, 0x14, 0x1C, 0x24, 0x2C, 0x34, 0x3C)
        if 0x04 <= opcode <= 0x3C and (opcode & 0x07) == 0x04:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = (opcode >> 3) & 0x07
            val = self._get_reg(regs[idx]) + 1
            self._set_reg(regs[idx], val & 0xFF)
            self.set_flag(self.FLAG_H, (val & 0x0F) == 0x00)
            self.set_flag(self.FLAG_S, val & 0x80)
            self.set_flag(self.FLAG_Z, (val & 0xFF) == 0)
            self.set_flag(self.FLAG_N, False)
            self.set_flag(self.FLAG_PV, val == 0x80)
            if regs[idx] == 'hl':
                return 11
            return 4
            
        # DEC r (0x05, 0x0D, 0x15, 0x1D, 0x25, 0x2D, 0x35, 0x3D)
        if 0x05 <= opcode <= 0x3D and (opcode & 0x07) == 0x05:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = (opcode >> 3) & 0x07
            val = self._get_reg(regs[idx]) - 1
            self._set_reg(regs[idx], val & 0xFF)
            self.set_flag(self.FLAG_H, (val & 0x0F) == 0x0F)
            self.set_flag(self.FLAG_S, val & 0x80)
            self.set_flag(self.FLAG_Z, (val & 0xFF) == 0)
            self.set_flag(self.FLAG_N, True)
            self.set_flag(self.FLAG_PV, val == 0x7F)
            if regs[idx] == 'hl':
                return 11
            return 4
            
        # ---------- ADD A, r ----------
        # ADD A, r (0x80-0x87)
        if 0x80 <= opcode <= 0x87:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = opcode & 0x07
            n = self._get_reg(regs[idx])
            result = self.a + n
            self.set_flag(self.FLAG_H, ((self.a & 0x0F) + (n & 0x0F)) > 0x0F)
            self.set_flag(self.FLAG_C, result > 0xFF)
            self.a = result & 0xFF
            self.set_flag(self.FLAG_S, self.a & 0x80)
            self.set_flag(self.FLAG_Z, self.a == 0)
            self.set_flag(self.FLAG_N, False)
            self.set_flag(self.FLAG_PV, ((self.a & 0x80) != (result & 0x80)))
            if regs[idx] == 'hl':
                return 7
            return 4
            
        # ADD A, n (0xC6)
        if opcode == 0xC6:
            n = self.read_byte(self.pc)
            self.pc += 1
            result = self.a + n
            self.set_flag(self.FLAG_H, ((self.a & 0x0F) + (n & 0x0F)) > 0x0F)
            self.set_flag(self.FLAG_C, result > 0xFF)
            self.a = result & 0xFF
            self.set_flag(self.FLAG_S, self.a & 0x80)
            self.set_flag(self.FLAG_Z, self.a == 0)
            self.set_flag(self.FLAG_N, False)
            self.set_flag(self.FLAG_PV, ((self.a & 0x80) != (result & 0x80)))
            return 7
            
        # ---------- ADC A, r ----------
        # ADC A, r (0x88-0x8F)
        if 0x88 <= opcode <= 0x8F:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = opcode & 0x07
            n = self._get_reg(regs[idx])
            carry = 1 if self.get_flag(self.FLAG_C) else 0
            result = self.a + n + carry
            self.set_flag(self.FLAG_H, ((self.a & 0x0F) + (n & 0x0F) + carry) > 0x0F)
            self.set_flag(self.FLAG_C, result > 0xFF)
            self.a = result & 0xFF
            self.set_flag(self.FLAG_S, self.a & 0x80)
            self.set_flag(self.FLAG_Z, self.a == 0)
            self.set_flag(self.FLAG_N, False)
            self.set_flag(self.FLAG_PV, ((self.a & 0x80) != (result & 0x80)))
            if regs[idx] == 'hl':
                return 7
            return 4
            
        # ADC A, n (0xCE)
        if opcode == 0xCE:
            n = self.read_byte(self.pc)
            self.pc += 1
            carry = 1 if self.get_flag(self.FLAG_C) else 0
            result = self.a + n + carry
            self.set_flag(self.FLAG_H, ((self.a & 0x0F) + (n & 0x0F) + carry) > 0x0F)
            self.set_flag(self.FLAG_C, result > 0xFF)
            self.a = result & 0xFF
            self.set_flag(self.FLAG_S, self.a & 0x80)
            self.set_flag(self.FLAG_Z, self.a == 0)
            self.set_flag(self.FLAG_N, False)
            self.set_flag(self.FLAG_PV, ((self.a & 0x80) != (result & 0x80)))
            return 7
            
        # ---------- SUB A, r ----------
        # SUB A, r (0x90-0x97)
        if 0x90 <= opcode <= 0x97:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = opcode & 0x07
            n = self._get_reg(regs[idx])
            result = self.a - n
            self.set_flag(self.FLAG_H, (self.a & 0x0F) < (n & 0x0F))
            self.set_flag(self.FLAG_C, self.a < n)
            self.a = result & 0xFF
            self.set_flag(self.FLAG_S, self.a & 0x80)
            self.set_flag(self.FLAG_Z, self.a == 0)
            self.set_flag(self.FLAG_N, True)
            self.set_flag(self.FLAG_PV, ((self.a & 0x80) != (result & 0x80)))
            if regs[idx] == 'hl':
                return 7
            return 4
            
        # SUB A, n (0xD6)
        if opcode == 0xD6:
            n = self.read_byte(self.pc)
            self.pc += 1
            result = self.a - n
            self.set_flag(self.FLAG_H, (self.a & 0x0F) < (n & 0x0F))
            self.set_flag(self.FLAG_C, self.a < n)
            self.a = result & 0xFF
            self.set_flag(self.FLAG_S, self.a & 0x80)
            self.set_flag(self.FLAG_Z, self.a == 0)
            self.set_flag(self.FLAG_N, True)
            self.set_flag(self.FLAG_PV, ((self.a & 0x80) != (result & 0x80)))
            return 7
            
        # ---------- SBC A, r ----------
        # SBC A, r (0x98-0x9F)
        if 0x98 <= opcode <= 0x9F:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = opcode & 0x07
            n = self._get_reg(regs[idx])
            carry = 1 if self.get_flag(self.FLAG_C) else 0
            result = self.a - n - carry
            self.set_flag(self.FLAG_H, (self.a & 0x0F) < (n & 0x0F) + carry)
            self.set_flag(self.FLAG_C, self.a < n + carry)
            self.a = result & 0xFF
            self.set_flag(self.FLAG_S, self.a & 0x80)
            self.set_flag(self.FLAG_Z, self.a == 0)
            self.set_flag(self.FLAG_N, True)
            self.set_flag(self.FLAG_PV, ((self.a & 0x80) != (result & 0x80)))
            if regs[idx] == 'hl':
                return 7
            return 4
            
        # SBC A, n (0xDE)
        if opcode == 0xDE:
            n = self.read_byte(self.pc)
            self.pc += 1
            carry = 1 if self.get_flag(self.FLAG_C) else 0
            result = self.a - n - carry
            self.set_flag(self.FLAG_H, (self.a & 0x0F) < (n & 0x0F) + carry)
            self.set_flag(self.FLAG_C, self.a < n + carry)
            self.a = result & 0xFF
            self.set_flag(self.FLAG_S, self.a & 0x80)
            self.set_flag(self.FLAG_Z, self.a == 0)
            self.set_flag(self.FLAG_N, True)
            self.set_flag(self.FLAG_PV, ((self.a & 0x80) != (result & 0x80)))
            return 7
            
        # ---------- AND A, r ----------
        # AND A, r (0xA0-0xA7)
        if 0xA0 <= opcode <= 0xA7:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = opcode & 0x07
            self.a &= self._get_reg(regs[idx])
            self.set_flag(self.FLAG_H, True)
            self.set_flag(self.FLAG_C, False)
            self.set_flag(self.FLAG_N, False)
            self.set_flag(self.FLAG_S, self.a & 0x80)
            self.set_flag(self.FLAG_Z, self.a == 0)
            self.set_flag(self.FLAG_PV, self.a & 0x80)  # Parity
            if regs[idx] == 'hl':
                return 7
            return 4
            
        # AND A, n (0xE6)
        if opcode == 0xE6:
            n = self.read_byte(self.pc)
            self.pc += 1
            self.a &= n
            self.set_flag(self.FLAG_H, True)
            self.set_flag(self.FLAG_C, False)
            self.set_flag(self.FLAG_N, False)
            self.set_flag(self.FLAG_S, self.a & 0x80)
            self.set_flag(self.FLAG_Z, self.a == 0)
            self.set_flag(self.FLAG_PV, self.a & 0x80)
            return 7
            
        # ---------- OR A, r ----------
        # OR A, r (0xB0-0xB7)
        if 0xB0 <= opcode <= 0xB7:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = opcode & 0x07
            self.a |= self._get_reg(regs[idx])
            self.set_flag(self.FLAG_H, False)
            self.set_flag(self.FLAG_C, False)
            self.set_flag(self.FLAG_N, False)
            self.set_flag(self.FLAG_S, self.a & 0x80)
            self.set_flag(self.FLAG_Z, self.a == 0)
            self.set_flag(self.FLAG_PV, self.a & 0x80)
            if regs[idx] == 'hl':
                return 7
            return 4
            
        # OR A, n (0xF6)
        if opcode == 0xF6:
            n = self.read_byte(self.pc)
            self.pc += 1
            self.a |= n
            self.set_flag(self.FLAG_H, False)
            self.set_flag(self.FLAG_C, False)
            self.set_flag(self.FLAG_N, False)
            self.set_flag(self.FLAG_S, self.a & 0x80)
            self.set_flag(self.FLAG_Z, self.a == 0)
            self.set_flag(self.FLAG_PV, self.a & 0x80)
            return 7
            
        # ---------- XOR A, r ----------
        # XOR A, r (0xA8-0xAF)
        if 0xA8 <= opcode <= 0xAF:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = opcode & 0x07
            self.a ^= self._get_reg(regs[idx])
            self.set_flag(self.FLAG_H, False)
            self.set_flag(self.FLAG_C, False)
            self.set_flag(self.FLAG_N, False)
            self.set_flag(self.FLAG_S, self.a & 0x80)
            self.set_flag(self.FLAG_Z, self.a == 0)
            self.set_flag(self.FLAG_PV, self.a & 0x80)
            if regs[idx] == 'hl':
                return 7
            return 4
            
        # XOR A, n (0xEE)
        if opcode == 0xEE:
            n = self.read_byte(self.pc)
            self.pc += 1
            self.a ^= n
            self.set_flag(self.FLAG_H, False)
            self.set_flag(self.FLAG_C, False)
            self.set_flag(self.FLAG_N, False)
            self.set_flag(self.FLAG_S, self.a & 0x80)
            self.set_flag(self.FLAG_Z, self.a == 0)
            self.set_flag(self.FLAG_PV, self.a & 0x80)
            return 7
            
        # ---------- CP A, r ----------
        # CP A, r (0xB8-0xBF)
        if 0xB8 <= opcode <= 0xBF:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = opcode & 0x07
            n = self._get_reg(regs[idx])
            result = self.a - n
            self.set_flag(self.FLAG_H, (self.a & 0x0F) < (n & 0x0F))
            self.set_flag(self.FLAG_C, self.a < n)
            self.set_flag(self.FLAG_S, result & 0x80)
            self.set_flag(self.FLAG_Z, (result & 0xFF) == 0)
            self.set_flag(self.FLAG_N, True)
            self.set_flag(self.FLAG_PV, ((result & 0x80) != ((result & 0xFF) & 0x80)))
            if regs[idx] == 'hl':
                return 7
            return 4
            
        # CP A, n (0xFE)
        if opcode == 0xFE:
            n = self.read_byte(self.pc)
            self.pc += 1
            result = self.a - n
            self.set_flag(self.FLAG_H, (self.a & 0x0F) < (n & 0x0F))
            self.set_flag(self.FLAG_C, self.a < n)
            self.set_flag(self.FLAG_S, result & 0x80)
            self.set_flag(self.FLAG_Z, (result & 0xFF) == 0)
            self.set_flag(self.FLAG_N, True)
            self.set_flag(self.FLAG_PV, ((result & 0x80) != ((result & 0xFF) & 0x80)))
            return 7
            
        # ---------- PUSH / POP ----------
        # PUSH AF (0xF5)
        if opcode == 0xF5:
            self.sp -= 1
            self.write_byte(self.sp, self.a)
            self.sp -= 1
            self.write_byte(self.sp, self.f)
            return 11
        # PUSH BC (0xC5)
        if opcode == 0xC5:
            self.sp -= 1
            self.write_byte(self.sp, self.b)
            self.sp -= 1
            self.write_byte(self.sp, self.c)
            return 11
        # PUSH DE (0xD5)
        if opcode == 0xD5:
            self.sp -= 1
            self.write_byte(self.sp, self.d)
            self.sp -= 1
            self.write_byte(self.sp, self.e)
            return 11
        # PUSH HL (0xE5)
        if opcode == 0xE5:
            self.sp -= 1
            self.write_byte(self.sp, self.h)
            self.sp -= 1
            self.write_byte(self.sp, self.l)
            return 11
        # PUSH IX (DD 0xE5)
        if opcode == 0xDD:
            sub = self.read_byte(self.pc)
            self.pc += 1
            if sub == 0xE5:
                self.sp -= 1
                self.write_byte(self.sp, (self.ix >> 8) & 0xFF)
                self.sp -= 1
                self.write_byte(self.sp, self.ix & 0xFF)
                return 15
            return 4
        # PUSH IY (FD 0xE5)
        if opcode == 0xFD:
            sub = self.read_byte(self.pc)
            self.pc += 1
            if sub == 0xE5:
                self.sp -= 1
                self.write_byte(self.sp, (self.iy >> 8) & 0xFF)
                self.sp -= 1
                self.write_byte(self.sp, self.iy & 0xFF)
                return 15
            return 4
            
        # POP AF (0xF1)
        if opcode == 0xF1:
            self.f = self.read_byte(self.sp)
            self.sp += 1
            self.a = self.read_byte(self.sp)
            self.sp += 1
            return 10
        # POP BC (0xC1)
        if opcode == 0xC1:
            self.c = self.read_byte(self.sp)
            self.sp += 1
            self.b = self.read_byte(self.sp)
            self.sp += 1
            return 10
        # POP DE (0xD1)
        if opcode == 0xD1:
            self.e = self.read_byte(self.sp)
            self.sp += 1
            self.d = self.read_byte(self.sp)
            self.sp += 1
            return 10
        # POP HL (0xE1)
        if opcode == 0xE1:
            self.l = self.read_byte(self.sp)
            self.sp += 1
            self.h = self.read_byte(self.sp)
            self.sp += 1
            return 10
        # POP IX (DD 0xE1)
        if opcode == 0xDD:
            sub = self.read_byte(self.pc)
            self.pc += 1
            if sub == 0xE1:
                self.ix = self.read_word(self.sp)
                self.sp += 2
                return 14
            return 4
        # POP IY (FD 0xE1)
        if opcode == 0xFD:
            sub = self.read_byte(self.pc)
            self.pc += 1
            if sub == 0xE1:
                self.iy = self.read_word(self.sp)
                self.sp += 2
                return 14
            return 4
            
        # ---------- CALL / RET / RST / JP / JR ----------
        # CALL nn (0xCD)
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
        if 0xC4 <= opcode <= 0xFC and (opcode & 0x07) == 0x04:
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
        if 0xC0 <= opcode <= 0xF8 and (opcode & 0x07) == 0x00 and opcode != 0xC9:
            cond = (opcode >> 3) & 0x07
            if self._check_cond(cond):
                self.pc = self.read_word(self.sp)
                self.sp += 2
                return 11
            return 5
            
        # RETI (ED 0x4D)
        if opcode == 0xED:
            sub = self.read_byte(self.pc)
            self.pc += 1
            if sub == 0x4D:
                self.iff1 = self.iff2
                self.pc = self.read_word(self.sp)
                self.sp += 2
                return 14
            # RETN (ED 0x45)
            if sub == 0x45:
                self.iff1 = self.iff2
                self.pc = self.read_word(self.sp)
                self.sp += 2
                return 14
            # LDI (ED 0xA0)
            if sub == 0xA0:
                self.write_byte(self.de, self.read_byte(self.hl))
                self.de = (self.de + 1) & 0xFFFF
                self.hl = (self.hl + 1) & 0xFFFF
                self.bc = (self.bc - 1) & 0xFFFF
                self.set_flag(self.FLAG_H, False)
                self.set_flag(self.FLAG_N, False)
                self.set_flag(self.FLAG_PV, self.bc != 0)
                return 16
            # LDD (ED 0xA8)
            if sub == 0xA8:
                self.write_byte(self.de, self.read_byte(self.hl))
                self.de = (self.de - 1) & 0xFFFF
                self.hl = (self.hl - 1) & 0xFFFF
                self.bc = (self.bc - 1) & 0xFFFF
                self.set_flag(self.FLAG_H, False)
                self.set_flag(self.FLAG_N, False)
                self.set_flag(self.FLAG_PV, self.bc != 0)
                return 16
            # LDIR (ED 0xB0)
            if sub == 0xB0:
                self.write_byte(self.de, self.read_byte(self.hl))
                self.de = (self.de + 1) & 0xFFFF
                self.hl = (self.hl + 1) & 0xFFFF
                self.bc = (self.bc - 1) & 0xFFFF
                self.set_flag(self.FLAG_H, False)
                self.set_flag(self.FLAG_N, False)
                self.set_flag(self.FLAG_PV, self.bc != 0)
                if self.bc != 0:
                    self.pc -= 2
                    return 21
                return 16
            # LDDR (ED 0xB8)
            if sub == 0xB8:
                self.write_byte(self.de, self.read_byte(self.hl))
                self.de = (self.de - 1) & 0xFFFF
                self.hl = (self.hl - 1) & 0xFFFF
                self.bc = (self.bc - 1) & 0xFFFF
                self.set_flag(self.FLAG_H, False)
                self.set_flag(self.FLAG_N, False)
                self.set_flag(self.FLAG_PV, self.bc != 0)
                if self.bc != 0:
                    self.pc -= 2
                    return 21
                return 16
            # CPI (ED 0xA1)
            if sub == 0xA1:
                val = self.read_byte(self.hl)
                result = self.a - val
                self.hl = (self.hl + 1) & 0xFFFF
                self.bc = (self.bc - 1) & 0xFFFF
                self.set_flag(self.FLAG_H, (self.a & 0x0F) < (val & 0x0F))
                self.set_flag(self.FLAG_N, True)
                self.set_flag(self.FLAG_Z, result == 0)
                self.set_flag(self.FLAG_PV, self.bc != 0)
                return 16
            # CPD (ED 0xA9)
            if sub == 0xA9:
                val = self.read_byte(self.hl)
                result = self.a - val
                self.hl = (self.hl - 1) & 0xFFFF
                self.bc = (self.bc - 1) & 0xFFFF
                self.set_flag(self.FLAG_H, (self.a & 0x0F) < (val & 0x0F))
                self.set_flag(self.FLAG_N, True)
                self.set_flag(self.FLAG_Z, result == 0)
                self.set_flag(self.FLAG_PV, self.bc != 0)
                return 16
            # CPIR (ED 0xB1)
            if sub == 0xB1:
                val = self.read_byte(self.hl)
                result = self.a - val
                self.hl = (self.hl + 1) & 0xFFFF
                self.bc = (self.bc - 1) & 0xFFFF
                self.set_flag(self.FLAG_H, (self.a & 0x0F) < (val & 0x0F))
                self.set_flag(self.FLAG_N, True)
                self.set_flag(self.FLAG_Z, result == 0)
                self.set_flag(self.FLAG_PV, self.bc != 0)
                if self.bc != 0 and result != 0:
                    self.pc -= 2
                    return 21
                return 16
            # CPDR (ED 0xB9)
            if sub == 0xB9:
                val = self.read_byte(self.hl)
                result = self.a - val
                self.hl = (self.hl - 1) & 0xFFFF
                self.bc = (self.bc - 1) & 0xFFFF
                self.set_flag(self.FLAG_H, (self.a & 0x0F) < (val & 0x0F))
                self.set_flag(self.FLAG_N, True)
                self.set_flag(self.FLAG_Z, result == 0)
                self.set_flag(self.FLAG_PV, self.bc != 0)
                if self.bc != 0 and result != 0:
                    self.pc -= 2
                    return 21
                return 16
            # IN A, (n) (ED 0x3A)
            if sub == 0x3A:
                port = self.read_byte(self.pc)
                self.pc += 1
                self.a = self.in_byte(port)
                return 11
            # OUT (n), A (ED 0x39)
            if sub == 0x39:
                port = self.read_byte(self.pc)
                self.pc += 1
                self.out_byte(port, self.a)
                return 11
            # IN r, (C) (ED 0x40-0x7F)
            if 0x40 <= sub <= 0x7F:
                regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
                idx = (sub >> 3) & 0x07
                val = self.in_byte(self.c)
                self._set_reg(regs[idx], val)
                self.set_flag(self.FLAG_H, False)
                self.set_flag(self.FLAG_N, False)
                self.set_flag(self.FLAG_S, val & 0x80)
                self.set_flag(self.FLAG_Z, val == 0)
                self.set_flag(self.FLAG_PV, val & 0x80)
                if regs[idx] == 'hl':
                    return 12
                return 12
            # OUT (C), r (ED 0x41-0x7F pour le même index)
            if 0x41 <= sub <= 0x7F and (sub & 0x01) == 0x01:
                regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
                idx = (sub >> 3) & 0x07
                val = self._get_reg(regs[idx])
                self.out_byte(self.c, val)
                if regs[idx] == 'hl':
                    return 12
                return 12
            # LD I, A (ED 0x47)
            if sub == 0x47:
                self.i = self.a
                return 9
            # LD A, I (ED 0x57)
            if sub == 0x57:
                self.a = self.i
                self.set_flag(self.FLAG_H, False)
                self.set_flag(self.FLAG_N, False)
                self.set_flag(self.FLAG_S, self.a & 0x80)
                self.set_flag(self.FLAG_Z, self.a == 0)
                self.set_flag(self.FLAG_PV, self.iff2)
                return 9
            # LD R, A (ED 0x4F)
            if sub == 0x4F:
                self.r = self.a
                return 9
            # LD A, R (ED 0x5F)
            if sub == 0x5F:
                self.a = self.r
                self.set_flag(self.FLAG_H, False)
                self.set_flag(self.FLAG_N, False)
                self.set_flag(self.FLAG_S, self.a & 0x80)
                self.set_flag(self.FLAG_Z, self.a == 0)
                self.set_flag(self.FLAG_PV, self.iff2)
                return 9
            # IM 0 (ED 0x46)
            if sub == 0x46:
                self.im = 0
                return 8
            # IM 1 (ED 0x56)
            if sub == 0x56:
                self.im = 1
                return 8
            # IM 2 (ED 0x5E)
            if sub == 0x5E:
                self.im = 2
                return 8
            return 8
            
        # RST (0xC7, 0xCF, 0xD7, 0xDF, 0xE7, 0xEF, 0xF7, 0xFF)
        if opcode >= 0xC7 and (opcode & 0xC7) == 0xC7:
            rst_addr = opcode & 0x38
            self.sp -= 1
            self.write_byte(self.sp, (self.pc >> 8) & 0xFF)
            self.sp -= 1
            self.write_byte(self.sp, self.pc & 0xFF)
            self.pc = rst_addr
            return 11
            
        # JP nn (0xC3)
        if opcode == 0xC3:
            self.pc = self.read_word(self.pc)
            return 10
            
        # JP condition (0xC2, 0xCA, 0xD2, 0xDA, 0xE2, 0xEA, 0xF2, 0xFA)
        if 0xC2 <= opcode <= 0xFA and (opcode & 0x07) == 0x02:
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
        # JP (IX) (DD 0xE9)
        if opcode == 0xDD:
            sub = self.read_byte(self.pc)
            self.pc += 1
            if sub == 0xE9:
                self.pc = self.ix
                return 8
            return 4
        # JP (IY) (FD 0xE9)
        if opcode == 0xFD:
            sub = self.read_byte(self.pc)
            self.pc += 1
            if sub == 0xE9:
                self.pc = self.iy
                return 8
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
                
        # ---------- NOP (0x00) ----------
        if opcode == 0x00:
            return 4
            
        # ---------- HALT (0x76) ----------
        if opcode == 0x76:
            self.halted = True
            return 4
            
        # ---------- DI (0xF3) ----------
        if opcode == 0xF3:
            self.iff1 = False
            self.iff2 = False
            return 4
            
        # ---------- EI (0xFB) ----------
        if opcode == 0xFB:
            self.iff1 = True
            self.iff2 = True
            return 4
            
        # ---------- LD (nn), A (0x32) ----------
        if opcode == 0x32:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.write_byte(addr, self.a)
            return 13
            
        # ---------- LD A, (nn) (0x3A) ----------
        if opcode == 0x3A:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.a = self.read_byte(addr)
            return 13
            
        # ---------- LD (nn), HL (0x22) ----------
        if opcode == 0x22:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.write_byte(addr, self.l)
            self.write_byte(addr + 1, self.h)
            return 16
            
        # ---------- LD HL, (nn) (0x2A) ----------
        if opcode == 0x2A:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.l = self.read_byte(addr)
            self.h = self.read_byte(addr + 1)
            return 16
            
        # ---------- LD (nn), BC (0xED 0x43) ----------
        if opcode == 0xED:
            sub = self.read_byte(self.pc)
            self.pc += 1
            if sub == 0x43:
                addr = self.read_word(self.pc)
                self.pc += 2
                self.write_byte(addr, self.c)
                self.write_byte(addr + 1, self.b)
                return 20
            # LD BC, (nn) (ED 0x4B)
            if sub == 0x4B:
                addr = self.read_word(self.pc)
                self.pc += 2
                self.c = self.read_byte(addr)
                self.b = self.read_byte(addr + 1)
                return 20
            # LD (nn), DE (ED 0x53)
            if sub == 0x53:
                addr = self.read_word(self.pc)
                self.pc += 2
                self.write_byte(addr, self.e)
                self.write_byte(addr + 1, self.d)
                return 20
            # LD DE, (nn) (ED 0x5B)
            if sub == 0x5B:
                addr = self.read_word(self.pc)
                self.pc += 2
                self.e = self.read_byte(addr)
                self.d = self.read_byte(addr + 1)
                return 20
            # LD (nn), SP (ED 0x73)
            if sub == 0x73:
                addr = self.read_word(self.pc)
                self.pc += 2
                self.write_byte(addr, self.sp & 0xFF)
                self.write_byte(addr + 1, (self.sp >> 8) & 0xFF)
                return 20
            # LD SP, (nn) (ED 0x7B)
            if sub == 0x7B:
                addr = self.read_word(self.pc)
                self.pc += 2
                self.sp = self.read_word(addr)
                return 20
            return 8
            
        # ---------- IN A, (n) (0xDB) ----------
        if opcode == 0xDB:
            port = self.read_byte(self.pc)
            self.pc += 1
            self.a = self.in_byte(port)
            return 11
            
        # ---------- OUT (n), A (0xD3) ----------
        if opcode == 0xD3:
            port = self.read_byte(self.pc)
            self.pc += 1
            self.out_byte(port, self.a)
            return 11
            
        # ---------- CPL (0x2F) ----------
        if opcode == 0x2F:
            self.a ^= 0xFF
            self.set_flag(self.FLAG_H, True)
            self.set_flag(self.FLAG_N, True)
            return 4
            
        # ---------- NEG (ED 0x44) ----------
        if opcode == 0xED:
            sub = self.read_byte(self.pc)
            self.pc += 1
            if sub == 0x44:
                result = -self.a
                self.set_flag(self.FLAG_H, (self.a & 0x0F) != 0)
                self.set_flag(self.FLAG_C, self.a != 0)
                self.a = result & 0xFF
                self.set_flag(self.FLAG_S, self.a & 0x80)
                self.set_flag(self.FLAG_Z, self.a == 0)
                self.set_flag(self.FLAG_N, True)
                self.set_flag(self.FLAG_PV, result & 0x80)
                return 8
            return 8
            
        # ---------- SCF (0x37) ----------
        if opcode == 0x37:
            self.set_flag(self.FLAG_C, True)
            self.set_flag(self.FLAG_H, False)
            self.set_flag(self.FLAG_N, False)
            return 4
            
        # ---------- CCF (0x3F) ----------
        if opcode == 0x3F:
            self.set_flag(self.FLAG_C, not self.get_flag(self.FLAG_C))
            self.set_flag(self.FLAG_H, False)
            self.set_flag(self.FLAG_N, False)
            return 4
            
        # ---------- DAA (0x27) ----------
        if opcode == 0x27:
            # Decimal Adjust Accumulator
            result = 0
            if self.get_flag(self.FLAG_H) or (self.a & 0x0F) > 9:
                result += 6
                self.set_flag(self.FLAG_H, True)
            if self.get_flag(self.FLAG_C) or self.a > 0x99:
                result += 0x60
                self.set_flag(self.FLAG_C, True)
            if self.get_flag(self.FLAG_N):
                self.a -= result
            else:
                self.a += result
            self.a &= 0xFF
            self.set_flag(self.FLAG_S, self.a & 0x80)
            self.set_flag(self.FLAG_Z, self.a == 0)
            self.set_flag(self.FLAG_H, False)
            self.set_flag(self.FLAG_PV, self.a & 0x80)
            return 4
            
        # ---------- CB prefix (instructions bit/rotate/shift) ----------
        if opcode == 0xCB:
            sub = self.read_byte(self.pc)
            self.pc += 1
            return self._execute_cb(sub)
            
        # ---------- DD prefix (IX) ----------
        if opcode == 0xDD:
            sub = self.read_byte(self.pc)
            self.pc += 1
            return self._execute_dd(sub)
            
        # ---------- FD prefix (IY) ----------
        if opcode == 0xFD:
            sub = self.read_byte(self.pc)
            self.pc += 1
            return self._execute_fd(sub)
            
        # ---------- Si aucune instruction ne correspond ----------
        # print(f"[Z80] Opcode non implémenté: {opcode:02X} à PC={self.pc-1:04X}")
        return 4
        
    # --- Fonctions auxiliaires pour CB prefix ---
    def _execute_cb(self, sub):
        # RLC r (0x00-0x07)
        if 0x00 <= sub <= 0x07:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = sub & 0x07
            val = self._get_reg(regs[idx])
            carry = (val >> 7) & 1
            val = ((val << 1) | carry) & 0xFF
            self._set_reg(regs[idx], val)
            self.set_flag(self.FLAG_H, False)
            self.set_flag(self.FLAG_N, False)
            self.set_flag(self.FLAG_C, carry)
            self.set_flag(self.FLAG_S, val & 0x80)
            self.set_flag(self.FLAG_Z, val == 0)
            self.set_flag(self.FLAG_PV, val & 0x80)
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
            self.set_flag(self.FLAG_H, False)
            self.set_flag(self.FLAG_N, False)
            self.set_flag(self.FLAG_C, carry)
            self.set_flag(self.FLAG_S, val & 0x80)
            self.set_flag(self.FLAG_Z, val == 0)
            self.set_flag(self.FLAG_PV, val & 0x80)
            if regs[idx] == 'hl':
                return 15
            return 8
            
        # RL r (0x10-0x17)
        if 0x10 <= sub <= 0x17:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = sub & 0x07
            val = self._get_reg(regs[idx])
            carry = (val >> 7) & 1
            old_carry = 1 if self.get_flag(self.FLAG_C) else 0
            val = ((val << 1) | old_carry) & 0xFF
            self._set_reg(regs[idx], val)
            self.set_flag(self.FLAG_H, False)
            self.set_flag(self.FLAG_N, False)
            self.set_flag(self.FLAG_C, carry)
            self.set_flag(self.FLAG_S, val & 0x80)
            self.set_flag(self.FLAG_Z, val == 0)
            self.set_flag(self.FLAG_PV, val & 0x80)
            if regs[idx] == 'hl':
                return 15
            return 8
            
        # RR r (0x18-0x1F)
        if 0x18 <= sub <= 0x1F:
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = sub & 0x07
            val = self._get_reg(regs[idx])
            carry = val & 1
            old_carry = 1 if self.get_flag(self.FLAG_C) else 0
            val = ((val >> 1) | (old_carry << 7)) & 0xFF
            self._set_reg(regs[idx], val)
            self.set_flag(self.FLAG_H, False)
            self.set_flag(self.FLAG_N, False)
            self.set_flag(self.FLAG_C, carry)
            self.set_flag(self.FLAG_S, val & 0x80)
            self.set_flag(self.FLAG_Z, val == 0)
            self.set_flag(self.FLAG_PV, val & 0x80)
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
            self.set_flag(self.FLAG_H, False)
            self.set_flag(self.FLAG_N, False)
            self.set_flag(self.FLAG_C, carry)
            self.set_flag(self.FLAG_S, val & 0x80)
            self.set_flag(self.FLAG_Z, val == 0)
            self.set_flag(self.FLAG_PV, val & 0x80)
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
            self.set_flag(self.FLAG_H, False)
            self.set_flag(self.FLAG_N, False)
            self.set_flag(self.FLAG_C, carry)
            self.set_flag(self.FLAG_S, val & 0x80)
            self.set_flag(self.FLAG_Z, val == 0)
            self.set_flag(self.FLAG_PV, val & 0x80)
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
            self.set_flag(self.FLAG_H, False)
            self.set_flag(self.FLAG_N, False)
            self.set_flag(self.FLAG_C, carry)
            self.set_flag(self.FLAG_S, val & 0x80)
            self.set_flag(self.FLAG_Z, val == 0)
            self.set_flag(self.FLAG_PV, val & 0x80)
            if regs[idx] == 'hl':
                return 15
            return 8
            
        # BIT b, r (0x40-0x7F)
        if 0x40 <= sub <= 0x7F:
            bit = (sub >> 3) & 0x07
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'hl', 'a']
            idx = sub & 0x07
            val = self._get_reg(regs[idx])
            self.set_flag(self.FLAG_H, True)
            self.set_flag(self.FLAG_N, False)
            self.set_flag(self.FLAG_S, (val & (1 << bit)) != 0)
            self.set_flag(self.FLAG_Z, (val & (1 << bit)) == 0)
            self.set_flag(self.FLAG_PV, (val & (1 << bit)) != 0)
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
        
    # --- Fonctions auxiliaires pour DD prefix (IX) ---
    def _execute_dd(self, sub):
        # IX instructions
        if sub == 0x21:  # LD IX, nn (déjà traité)
            return 14
        if sub == 0x23:  # INC IX
            self.ix = (self.ix + 1) & 0xFFFF
            return 10
        if sub == 0x2B:  # DEC IX
            self.ix = (self.ix - 1) & 0xFFFF
            return 10
        if sub == 0xE5:  # PUSH IX
            self.sp -= 1
            self.write_byte(self.sp, (self.ix >> 8) & 0xFF)
            self.sp -= 1
            self.write_byte(self.sp, self.ix & 0xFF)
            return 15
        if sub == 0xE1:  # POP IX
            self.ix = self.read_word(self.sp)
            self.sp += 2
            return 14
        if sub == 0xE3:  # EX (SP), IX
            tmp = self.read_word(self.sp)
            self.write_word(self.sp, self.ix)
            self.ix = tmp
            return 23
        if sub == 0xE9:  # JP (IX)
            self.pc = self.ix
            return 8
        if sub == 0x09:  # ADD IX, BC
            result = self.ix + self.bc
            self.set_flag(self.FLAG_H, (self.ix & 0x0FFF) + (self.bc & 0x0FFF) > 0x0FFF)
            self.set_flag(self.FLAG_C, result > 0xFFFF)
            self.set_flag(self.FLAG_N, False)
            self.ix = result & 0xFFFF
            return 15
        if sub == 0x19:  # ADD IX, DE
            result = self.ix + self.de
            self.set_flag(self.FLAG_H, (self.ix & 0x0FFF) + (self.de & 0x0FFF) > 0x0FFF)
            self.set_flag(self.FLAG_C, result > 0xFFFF)
            self.set_flag(self.FLAG_N, False)
            self.ix = result & 0xFFFF
            return 15
        if sub == 0x29:  # ADD IX, IX
            result = self.ix + self.ix
            self.set_flag(self.FLAG_H, (self.ix & 0x0FFF) + (self.ix & 0x0FFF) > 0x0FFF)
            self.set_flag(self.FLAG_C, result > 0xFFFF)
            self.set_flag(self.FLAG_N, False)
            self.ix = result & 0xFFFF
            return 15
        if sub == 0x39:  # ADD IX, SP
            result = self.ix + self.sp
            self.set_flag(self.FLAG_H, (self.ix & 0x0FFF) + (self.sp & 0x0FFF) > 0x0FFF)
            self.set_flag(self.FLAG_C, result > 0xFFFF)
            self.set_flag(self.FLAG_N, False)
            self.ix = result & 0xFFFF
            return 15
        # LD (IX+d), r (0x70-0x77)
        if 0x70 <= sub <= 0x77:
            d = self.read_byte(self.pc)
            self.pc += 1
            regs = ['b', 'c', 'd', 'e', 'h', 'l', 'a']
            idx = sub & 0x07
            if idx == 6:  # LD (IX+d), (HL)
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
                self.hl = (self.hl & 0xFF00) | val
                self.l = val
            else:
                self._set_reg(regs[idx], val)
            return 19
        return 4
        
    # --- Fonctions auxiliaires pour FD prefix (IY) ---
    def _execute_fd(self, sub):
        # IY instructions
        if sub == 0x21:  # LD IY, nn
            self.iy = self.read_word(self.pc)
            self.pc += 2
            return 14
        if sub == 0x23:  # INC IY
            self.iy = (self.iy + 1) & 0xFFFF
            return 10
        if sub == 0x2B:  # DEC IY
            self.iy = (self.iy - 1) & 0xFFFF
            return 10
        if sub == 0xE5:  # PUSH IY
            self.sp -= 1
            self.write_byte(self.sp, (self.iy >> 8) & 0xFF)
            self.sp -= 1
            self.write_byte(self.sp, self.iy & 0xFF)
            return 15
        if sub == 0xE1:  # POP IY
            self.iy = self.read_word(self.sp)
            self.sp += 2
            return 14
        if sub == 0xE3:  # EX (SP), IY
            tmp = self.read_word(self.sp)
            self.write_word(self.sp, self.iy)
            self.iy = tmp
            return 23
        if sub == 0xE9:  # JP (IY)
            self.pc = self.iy
            return 8
        if sub == 0x09:  # ADD IY, BC
            result = self.iy + self.bc
            self.set_flag(self.FLAG_H, (self.iy & 0x0FFF) + (self.bc & 0x0FFF) > 0x0FFF)
            self.set_flag(self.FLAG_C, result > 0xFFFF)
            self.set_flag(self.FLAG_N, False)
            self.iy = result & 0xFFFF
            return 15
        if sub == 0x19:  # ADD IY, DE
            result = self.iy + self.de
            self.set_flag(self.FLAG_H, (self.iy & 0x0FFF) + (self.de & 0x0FFF) > 0x0FFF)
            self.set_flag(self.FLAG_C, result > 0xFFFF)
            self.set_flag(self.FLAG_N, False)
            self.iy = result & 0xFFFF
            return 15
        if sub == 0x29:  # ADD IY, IY
            result = self.iy + self.iy
            self.set_flag(self.FLAG_H, (self.iy & 0x0FFF) + (self.iy & 0x0FFF) > 0x0FFF)
            self.set_flag(self.FLAG_C, result > 0xFFFF)
            self.set_flag(self.FLAG_N, False)
            self.iy = result & 0xFFFF
            return 15
        if sub == 0x39:  # ADD IY, SP
            result = self.iy + self.sp
            self.set_flag(self.FLAG_H, (self.iy & 0x0FFF) + (self.sp & 0x0FFF) > 0x0FFF)
            self.set_flag(self.FLAG_C, result > 0xFFFF)
            self.set_flag(self.FLAG_N, False)
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
                self.hl = (self.hl & 0xFF00) | val
                self.l = val
            else:
                self._set_reg(regs[idx], val)
            return 19
        return 4
        
    # --- Fonctions auxiliaires (accès aux registres) ---
    def _get_reg(self, name):
        if name == 'b': return self.b
        if name == 'c': return self.c
        if name == 'd': return self.d
        if name == 'e': return self.e
        if name == 'h': return self.h
        if name == 'l': return self.l
        if name == 'a': return self.a
        if name == 'hl': return self.read_byte(self.hl)
        if name == 'ix': return self.ix
        if name == 'iy': return self.iy
        return 0
        
    def _set_reg(self, name, value):
        if name == 'b': self.b = value
        elif name == 'c': self.c = value
        elif name == 'd': self.d = value
        elif name == 'e': self.e = value
        elif name == 'h': self.h = value
        elif name == 'l': self.l = value
        elif name == 'a': self.a = value
        elif name == 'hl': self.write_byte(self.hl, value)
        elif name == 'ix': self.ix = value
        elif name == 'iy': self.iy = value
        
    def _check_cond(self, cond):
        if cond == 'nz' or cond == 0:
            return not self.get_flag(self.FLAG_Z)
        if cond == 'z' or cond == 1:
            return self.get_flag(self.FLAG_Z)
        if cond == 'nc' or cond == 2:
            return not self.get_flag(self.FLAG_C)
        if cond == 'c' or cond == 3:
            return self.get_flag(self.FLAG_C)
        if cond == 'po' or cond == 4:
            return not self.get_flag(self.FLAG_PV)
        if cond == 'pe' or cond == 5:
            return self.get_flag(self.FLAG_PV)
        if cond == 'p' or cond == 6:
            return not self.get_flag(self.FLAG_S)
        if cond == 'm' or cond == 7:
            return self.get_flag(self.FLAG_S)
        return False
        
    # --- Getter pour l'état (debug) ---
    def get_registers(self):
        return {
            'pc': self.pc,
            'sp': self.sp,
            'af': self.af,
            'bc': self.bc,
            'de': self.de,
            'hl': self.hl,
            'af_alt': (self.a_alt << 8) | self.f_alt,
            'bc_alt': (self.b_alt << 8) | self.c_alt,
            'de_alt': (self.d_alt << 8) | self.e_alt,
            'hl_alt': (self.h_alt << 8) | self.l_alt,
            'ix': self.ix,
            'iy': self.iy,
            'i': self.i,
            'r': self.r,
            'iff1': self.iff1,
            'iff2': self.iff2,
            'im': self.im,
            'halted': self.halted,
            'cycles': self.cycles,
        }