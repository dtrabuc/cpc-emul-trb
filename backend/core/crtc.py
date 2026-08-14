class CRTC6845:
    """
    CRTC 6845 tel que cable dans le CPC464.

    Port I/O (bits A9,A8 du port 16 bits) :
        00 (0xBCxx) -> ecriture : selection de registre (index)
        01 (0xBDxx) -> ecriture : donnee dans le registre selectionne
        10 (0xBExx) -> lecture  : registre de statut (non implemente ici)
        11 (0xBFxx) -> lecture  : donnee du registre selectionne

    La logique de comptage (clock()) est portee directement de
    CPCSharp.Core/CRTC.cs (Nathan Randle, licence MIT), adaptee pour
    etre appelee cycle par cycle depuis tick(cycles).

    Simplification assumee : le CRTC est ici cadence a raison d'un
    "clock()" toutes les 4 cycles Z80 (le Z80 du CPC tourne a 4 MHz,
    le CRTC/Gate Array a une frequence caractere de 1 MHz). Le vrai
    hardware utilise un signal CCLK derive du Gate Array ; cette
    approximation suffit pour un affichage et un timing d'IT corrects
    a l'echelle de la trame, mais n'est pas cycle-exacte au T-state pres.
    """

    CPU_CYCLES_PER_CRTC_CLOCK = 4

    def __init__(self):
        self.regs = [0] * 32
        self.index = 0

        # Signaux de sortie observables par le Gate Array / PPI
        self.hsync = False
        self.vsync = False
        self.dispen = False  # True = zone visible (l'ancien "DISP" du C#)

        # Registres decodes (memes noms que CPCSharp.Core/CRTC.cs)
        self._horizontal_total = 0
        self._horizontal_displayed = 0
        self._horizontal_sync_position = 0
        self._hsync_width = 14  # TODO: extraire R3 bits 0-3 comme le hardware reel
        self._vsync_width = 8   # TODO: extraire R3 bits 4-7 sur les modeles qui le supportent

        self._vertical_total = 0
        self._vertical_total_adjust = 0
        self._vertical_displayed = 0
        self._vertical_sync_position = 0
        self._max_raster_address = 0

        self._start_address_high = 0
        self._start_address_low = 0

        self._clock_cycles_this_line = 0
        self._lines_completed = 0
        self.row_address = 0
        self.memory_address = 0

        self._cpu_cycle_accumulator = 0

    def reset(self):
        self.__init__()

    # --- Acces CPU -------------------------------------------------

    def write(self, port, value):
        selector = (port >> 8) & 0x03
        if selector == 0b00:
            self.index = value & 0x1F
        elif selector == 0b01:
            self._write_register(self.index, value & 0xFF)

    def read(self, port):
        selector = (port >> 8) & 0x03
        if selector == 0b11:
            return self.regs[self.index] if self.index < 32 else 0
        return 0xFF

    def _write_register(self, index, value):
        if index < 32:
            self.regs[index] = value

        if index == 0:
            self._horizontal_total = value
        elif index == 1:
            self._horizontal_displayed = value
        elif index == 2:
            self._horizontal_sync_position = value
        elif index == 4:
            self._vertical_total = value
        elif index == 5:
            self._vertical_total_adjust = value
        elif index == 6:
            self._vertical_displayed = value
        elif index == 7:
            self._vertical_sync_position = value
        elif index == 9:
            self._max_raster_address = value
        elif index == 12:
            self._start_address_high = value
        elif index == 13:
            self._start_address_low = value
        # Les autres registres (curseur, R3 largeurs de sync, etc.) sont
        # stockes dans self.regs mais pas encore interpretes -- a completer
        # si besoin (curseur clignotant, largeur HSYNC/VSYNC variable...).

    # --- Proprietes derivees (portees de CRTC.cs) -------------------

    @property
    def char_position(self):
        """Position horizontale courante, en caracteres, sur la ligne (0-based)."""
        return self._clock_cycles_this_line

    @property
    def line_position(self):
        """Numero de ligne de balayage courante dans la trame (0-based)."""
        return self._lines_completed

    @property
    def total_scan_lines(self):
        return (self._vertical_total * (self._max_raster_address + 1)) + self._vertical_total_adjust

    @property
    def in_hsync_region(self):
        start = self._horizontal_sync_position - 1
        return start <= self._clock_cycles_this_line < start + self._hsync_width

    @property
    def in_vsync_region(self):
        start = self._vertical_sync_position * (self._max_raster_address + 1)
        return start <= self._lines_completed < start + self._vsync_width

    @property
    def in_dispen_region(self):
        return (self._clock_cycles_this_line >= self._horizontal_displayed
                or self._lines_completed >= self._vertical_displayed * (self._max_raster_address + 1))

    # --- Horloge -----------------------------------------------------

    def tick(self, cpu_cycles):
        """Avance le CRTC de cpu_cycles cycles Z80 (voir note de classe)."""
        self._cpu_cycle_accumulator += cpu_cycles
        while self._cpu_cycle_accumulator >= self.CPU_CYCLES_PER_CRTC_CLOCK:
            self._cpu_cycle_accumulator -= self.CPU_CYCLES_PER_CRTC_CLOCK
            self._clock()

    def _clock(self):
        self.hsync = self.in_hsync_region

        if not self.dispen:
            if (self._clock_cycles_this_line == self._horizontal_displayed
                    and self.row_address != self._max_raster_address):
                self.memory_address -= self._horizontal_displayed

        if self._clock_cycles_this_line > self._horizontal_total:
            if self.row_address == self._max_raster_address:
                self.row_address = 0
            else:
                self.row_address += 1
            self._clock_cycles_this_line = 0
            self._lines_completed += 1

        if self.in_vsync_region:
            self.vsync = True
            self.memory_address = (self._start_address_high << 8) | self._start_address_low
        else:
            self.vsync = False

        if self._lines_completed >= self.total_scan_lines:
            self.row_address = 0
            self._lines_completed = 0

        if not self.dispen:
            self.memory_address += 1

        self.dispen = self.in_dispen_region
        self._clock_cycles_this_line += 1

    @staticmethod
    def active_at_address(address):
        significant = address & 0xFF00
        return 0xBC00 <= significant <= 0xBF00