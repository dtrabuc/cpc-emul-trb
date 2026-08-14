class Z80CPU:
    def __init__(self):
        self.memory = None
        self.io_read = None
        self.io_write = None
        self.reset()
        
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
        self.halted = False
        self.cycles = 0
        
    @property
    def af(self): return (self.a << 8) | self.f
    @af.setter
    def af(self, v): self.a = (v >> 8) & 0xFF; self.f = v & 0xFF
    @property
    def bc(self): return (self.b << 8) | self.c
    @bc.setter
    def bc(self, v): self.b = (v >> 8) & 0xFF; self.c = v & 0xFF
    @property
    def de(self): return (self.d << 8) | self.e
    @de.setter
    def de(self, v): self.d = (v >> 8) & 0xFF; self.e = v & 0xFF
    @property
    def hl(self): return (self.h << 8) | self.l
    @hl.setter
    def hl(self, v): self.h = (v >> 8) & 0xFF; self.l = v & 0xFF
    
    FLAG_C = 0x01
    FLAG_N = 0x02
    FLAG_PV = 0x04
    FLAG_H = 0x10
    FLAG_Z = 0x40
    FLAG_S = 0x80
    
    def read_byte(self, addr):
        return self.memory.read_byte(addr) if self.memory else 0xFF
        
    def write_byte(self, addr, v):
        if self.memory: self.memory.write_byte(addr, v)
        
    def read_word(self, addr):
        return self.read_byte(addr) | (self.read_byte(addr+1) << 8)
        
    def write_word(self, addr, v):
        self.write_byte(addr, v & 0xFF)
        self.write_byte(addr+1, (v >> 8) & 0xFF)
        
    def in_byte(self, port):
        return self.io_read(port) if self.io_read else 0xFF
        
    def out_byte(self, port, v):
        if self.io_write: self.io_write(port, v)
        
    def set_flag(self, flag, v):
        if v: self.f |= flag
        else: self.f &= ~flag
        
    def get_flag(self, flag):
        return (self.f & flag) != 0
        
    def step(self):
        if self.halted:
            return 1
            
        opcode = self.read_byte(self.pc)
        self.pc += 1
        cycles = self.execute(opcode)
        self.cycles += cycles
        return cycles
        
    def execute(self, opcode):
        # NOP
        if opcode == 0x00:
            return 4
            
        # LD BC, nn
        if opcode == 0x01:
            self.bc = self.read_word(self.pc)
            self.pc += 2
            return 10
            
        # LD (BC), A
        if opcode == 0x02:
            self.write_byte(self.bc, self.a)
            return 7
            
        # INC BC
        if opcode == 0x03:
            self.bc = (self.bc + 1) & 0xFFFF
            return 6
            
        # INC B
        if opcode == 0x04:
            v = (self.b + 1) & 0xFF
            self.set_flag(self.FLAG_H, (self.b & 0x0F) == 0x0F)
            self.b = v
            self.set_flag(self.FLAG_S, v & 0x80)
            self.set_flag(self.FLAG_Z, v == 0)
            self.set_flag(self.FLAG_N, False)
            self.set_flag(self.FLAG_PV, v == 0x7F)
            return 4
            
        # DEC B
        if opcode == 0x05:
            v = (self.b - 1) & 0xFF
            self.set_flag(self.FLAG_H, (self.b & 0x0F) == 0x00)
            self.b = v
            self.set_flag(self.FLAG_S, v & 0x80)
            self.set_flag(self.FLAG_Z, v == 0)
            self.set_flag(self.FLAG_N, True)
            self.set_flag(self.FLAG_PV, v == 0x80)
            return 4
            
        # LD B, n
        if opcode == 0x06:
            self.b = self.read_byte(self.pc)
            self.pc += 1
            return 7
            
        # LD DE, nn
        if opcode == 0x11:
            self.de = self.read_word(self.pc)
            self.pc += 2
            return 10
            
        # LD HL, nn
        if opcode == 0x21:
            self.hl = self.read_word(self.pc)
            self.pc += 2
            return 10
            
        # LD SP, nn
        if opcode == 0x31:
            self.sp = self.read_word(self.pc)
            self.pc += 2
            return 10
            
        # LD A, n
        if opcode == 0x3E:
            self.a = self.read_byte(self.pc)
            self.pc += 1
            return 7
            
        # LD A, (HL)
        if opcode == 0x7E:
            self.a = self.read_byte(self.hl)
            return 7
            
        # LD (HL), A
        if opcode == 0x77:
            self.write_byte(self.hl, self.a)
            return 7
            
        # LD (nn), HL
        if opcode == 0x22:
            addr = self.read_word(self.pc)
            self.write_byte(addr, self.l)
            self.write_byte(addr + 1, self.h)
            self.pc += 2
            return 16
            
        # LD HL, (nn)
        if opcode == 0x2A:
            addr = self.read_word(self.pc)
            self.l = self.read_byte(addr)
            self.h = self.read_byte(addr + 1)
            self.pc += 2
            return 16
            
        # JR
        if opcode == 0x18:
            offset = self.read_byte(self.pc)
            self.pc += 1
            if offset & 0x80:
                self.pc -= (0x100 - offset)
            else:
                self.pc += offset
            return 12
            
        # CALL nn
        if opcode == 0xCD:
            addr = self.read_word(self.pc)
            self.pc += 2
            self.sp -= 1
            self.write_byte(self.sp, (self.pc >> 8) & 0xFF)
            self.sp -= 1
            self.write_byte(self.sp, self.pc & 0xFF)
            self.pc = addr
            return 17
            
        # RET
        if opcode == 0xC9:
            self.pc = self.read_byte(self.sp) | (self.read_byte(self.sp + 1) << 8)
            self.sp += 2
            return 10
            
        # PUSH AF
        if opcode == 0xF5:
            self.sp -= 1
            self.write_byte(self.sp, self.a)
            self.sp -= 1
            self.write_byte(self.sp, self.f)
            return 11
            
        # POP AF
        if opcode == 0xF1:
            self.f = self.read_byte(self.sp)
            self.sp += 1
            self.a = self.read_byte(self.sp)
            self.sp += 1
            return 10
            
        # HALT
        if opcode == 0x76:
            self.halted = True
            return 4
            
        # ADD A, n
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
            self.set_flag(self.FLAG_PV, (result & 0x80) != (self.a & 0x80))
            return 7
            
        # ADD A, (HL)
        if opcode == 0x86:
            n = self.read_byte(self.hl)
            result = self.a + n
            self.set_flag(self.FLAG_H, ((self.a & 0x0F) + (n & 0x0F)) > 0x0F)
            self.set_flag(self.FLAG_C, result > 0xFF)
            self.a = result & 0xFF
            self.set_flag(self.FLAG_S, self.a & 0x80)
            self.set_flag(self.FLAG_Z, self.a == 0)
            self.set_flag(self.FLAG_N, False)
            self.set_flag(self.FLAG_PV, (result & 0x80) != (self.a & 0x80))
            return 7
            
        # SUB A, n
        if opcode == 0xD6:
            n = self.read_byte(self.pc)
            self.pc += 1
            result = self.a - n
            self.set_flag(self.FLAG_H, (self.a & 0x0F) < (n & 0x0F))
            self.set_flag(self.FLAG_C, result < 0)
            self.a = result & 0xFF
            self.set_flag(self.FLAG_S, self.a & 0x80)
            self.set_flag(self.FLAG_Z, self.a == 0)
            self.set_flag(self.FLAG_N, True)
            self.set_flag(self.FLAG_PV, (result & 0x80) != (self.a & 0x80))
            return 7
            
        # CP A, n
        if opcode == 0xFE:
            n = self.read_byte(self.pc)
            self.pc += 1
            result = self.a - n
            self.set_flag(self.FLAG_H, (self.a & 0x0F) < (n & 0x0F))
            self.set_flag(self.FLAG_C, result < 0)
            self.set_flag(self.FLAG_S, result & 0x80)
            self.set_flag(self.FLAG_Z, (result & 0xFF) == 0)
            self.set_flag(self.FLAG_N, True)
            self.set_flag(self.FLAG_PV, (result & 0x80) != ((result & 0xFF) & 0x80))
            return 7
            
        # INC HL
        if opcode == 0x23:
            self.hl = (self.hl + 1) & 0xFFFF
            return 6
            
        # DEC HL
        if opcode == 0x2B:
            self.hl = (self.hl - 1) & 0xFFFF
            return 6
            
        # LD DE, (nn) - utilisé par BASIC
        if opcode == 0xED:
            # On regarde le byte suivant pour les instructions ED
            sub_op = self.read_byte(self.pc)
            self.pc += 1
            # LD DE, (nn)
            if sub_op == 0x5B:
                addr = self.read_word(self.pc)
                self.pc += 2
                self.e = self.read_byte(addr)
                self.d = self.read_byte(addr + 1)
                return 20
            # LD (nn), DE
            if sub_op == 0x53:
                addr = self.read_word(self.pc)
                self.pc += 2
                self.write_byte(addr, self.e)
                self.write_byte(addr + 1, self.d)
                return 20
            # RETI / RETN
            if sub_op in [0x4D, 0x45]:
                self.iff1 = self.iff2
                self.pc = self.read_byte(self.sp) | (self.read_byte(self.sp + 1) << 8)
                self.sp += 2
                return 14
            # LD I, A
            if sub_op == 0x47:
                self.i = self.a
                return 9
            # LD A, I
            if sub_op == 0x57:
                self.a = self.i
                self.set_flag(self.FLAG_S, self.a & 0x80)
                self.set_flag(self.FLAG_Z, self.a == 0)
                self.set_flag(self.FLAG_H, False)
                self.set_flag(self.FLAG_N, False)
                self.set_flag(self.FLAG_PV, self.iff2)
                return 9
            # LD R, A
            if sub_op == 0x4F:
                self.r = self.a
                return 9
            # LD A, R
            if sub_op == 0x5F:
                self.a = self.r
                self.set_flag(self.FLAG_S, self.a & 0x80)
                self.set_flag(self.FLAG_Z, self.a == 0)
                self.set_flag(self.FLAG_H, False)
                self.set_flag(self.FLAG_N, False)
                self.set_flag(self.FLAG_PV, self.iff2)
                return 9
            # IN/OUT (simplifiés)
            if sub_op == 0x40:  # IN B, (C)
                self.b = self.in_byte(self.bc & 0xFF)
                return 12
            if sub_op == 0x41:  # OUT (C), B
                self.out_byte(self.bc & 0xFF, self.b)
                return 12
            # On renvoie 8 cycles pour les autres ED
            return 8
            
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
            
        # RST
        if 0xC7 <= opcode <= 0xFF and opcode & 0xC7 == 0xC7:
            rst_addr = opcode & 0x38
            self.sp -= 1
            self.write_byte(self.sp, (self.pc >> 8) & 0xFF)
            self.sp -= 1
            self.write_byte(self.sp, self.pc & 0xFF)
            self.pc = rst_addr
            return 11
            
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
            
        # JP nn
        if opcode == 0xC3:
            self.pc = self.read_word(self.pc)
            return 10
            
        # JP (HL)
        if opcode == 0xE9:
            self.pc = self.hl
            return 4
            
        # Si on arrive là, opcode non implémenté
        print(f"[Z80] Opcode non implémenté: {opcode:02X} à PC={self.pc-1:04X}")
        return 4