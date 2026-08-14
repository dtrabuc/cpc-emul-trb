# core/gate_array.py
#
# Portage de CPCSharp.Core/GateArray.cs (Nathan Randle, licence MIT) :
# decodage reel des modes video 0/1/2, palette 27 couleurs (approximee
# a partir de la meme table RGB que la version C#), selection de
# crayon/bordure, commutation ROM haute/basse, et generation des
# interruptions 300 Hz (toutes les 52 HSYNC, avec le decalage VSYNC).
#
# Simplification assumee (documentee aussi dans crtc.py) : le Gate Array
# est ici cadence a un "clock interne" toutes les 4 cycles Z80, au lieu
# du vrai signal 16 MHz derive du hardware. Suffisant pour un affichage
# correct et un timing d'IT correct a l'echelle de la trame.

ColourMap = [
    "#7f7f7f", "#7f7f7f", "#00ff7f", "#ffff7f",
    "#00007f", "#ff007f", "#007f7f", "#ff7f7f",
    "#ff007f", "#ffff7f", "#ffff00", "#ffffff",
    "#ff0000", "#ff00ff", "#ff7f00", "#ff7fff",
    "#00007f", "#00ff7f", "#00ff00", "#00ffff",
    "#000000", "#0000ff", "#007f00", "#007fff",
    "#7f007f", "#7fff7f", "#7fff00", "#7fffff",
    "#7f0000", "#7f00ff", "#7f7f00", "#7f7fff",
]


class GateArray:
    def __init__(self, memory=None, crtc=None):
        self.memory = memory
        self.crtc = crtc

        self.lower_rom_enabled = True
        self.upper_rom_enabled = True
        self.screen_mode = 1

        self._pen_colours = [0] * 16
        self._border_colour = 0
        self._selected_pen_index = 0  # -1 = bordure selectionnee

        self._hsyncs_since_vsync_started = 0
        self._hsync_completed_count = 0
        self.interrupt = False

        self._prev_hsync = False
        self._prev_vsync = False

        self._cpu_cycle_accumulator = 0

        # Framebuffer RGB (liste de lignes de couleurs hexa), redimensionne
        # au fil de l'eau selon les registres CRTC programmes par la ROM.
        self.width = 384
        self.height = 272
        self.screen = [["#000000"] * self.width for _ in range(self.height)]

    def reset(self):
        self.lower_rom_enabled = True
        self.upper_rom_enabled = True
        self._pen_colours = [0] * 16
        self._border_colour = 0
        self.interrupt = False
        self._hsync_completed_count = 0
        self._hsyncs_since_vsync_started = 0
        self._cpu_cycle_accumulator = 0
        self.screen = [["#000000"] * self.width for _ in range(self.height)]

    # --- Nombre de pixels produits par octet video, selon le mode ---

    @property
    def pixels_per_byte(self):
        return {0: 2, 1: 4, 2: 8}.get(self.screen_mode, 0)

    # --- Acces CPU (ecriture I/O uniquement, la lecture n'existe pas) ---

    def write(self, value):
        function_select = value >> 6
        if function_select == 0:
            self._select_pen(value)
        elif function_select == 1:
            self._select_pen_colour(value)
        elif function_select == 2:
            self._screen_mode_rom_config(value)
        # function_select == 3 : gestion RAM (banking) -- non geree, comme
        # dans la version C# de reference.

    @staticmethod
    def active_at_address(address):
        # Actif quand les 2 bits de poids fort de l'adresse valent 01
        return (address & 0xC000) == 0x4000

    def _select_pen(self, value):
        if value & 0x10:
            self._selected_pen_index = -1  # bordure
        else:
            self._selected_pen_index = value & 0x0F

    def _select_pen_colour(self, value):
        colour = value & 0x1F
        if self._selected_pen_index == -1:
            self._border_colour = colour
        else:
            self._pen_colours[self._selected_pen_index] = colour

    def _screen_mode_rom_config(self, value):
        if value & 0x10:
            self._hsync_completed_count = 0  # reset compteur d'IT

        self.lower_rom_enabled = (value & 0x04) == 0
        self.upper_rom_enabled = (value & 0x08) == 0

        if self.memory is not None:
            self.memory.lower_rom_enabled = self.lower_rom_enabled
            self.memory.upper_rom_enabled = self.upper_rom_enabled

        self.screen_mode = value & 0x03

    # --- Horloge -------------------------------------------------------

    def tick(self, cpu_cycles):
        self._cpu_cycle_accumulator += cpu_cycles
        while self._cpu_cycle_accumulator >= 4:
            self._cpu_cycle_accumulator -= 4
            self._clock()

    def _clock(self):
        if self.crtc is None:
            return

        hsync, vsync, dispen = self.crtc.hsync, self.crtc.vsync, self.crtc.dispen

        # Front montant VSYNC : redemarre le compteur "hsyncs depuis vsync"
        if vsync and not self._prev_vsync:
            self._hsyncs_since_vsync_started = 0

        # Front descendant HSYNC : une ligne de plus est terminee
        if not hsync and self._prev_hsync:
            self._hsync_completed_count += 1
            if vsync:
                self._hsyncs_since_vsync_started += 1

        self._prev_hsync = hsync
        self._prev_vsync = vsync

        self._check_hsync_interrupt()
        self._check_vsync_interrupt()

        if not (hsync or vsync):
            self._render_pixels(dispen)

    def _check_hsync_interrupt(self):
        if self._hsync_completed_count == 52:
            self._hsync_completed_count = 0
            self.interrupt = True

    def _check_vsync_interrupt(self):
        if self._hsyncs_since_vsync_started == 2:
            if self._hsync_completed_count >= 32:
                self.interrupt = True
            self._hsyncs_since_vsync_started += 1
            self._hsync_completed_count = 0

    def acknowledge_interrupt(self):
        """A appeler par l'emulateur une fois l'IT prise en compte par le CPU."""
        self.interrupt = False
        self._hsync_completed_count &= 0b00011111

    # --- Generation des pixels ------------------------------------------

    def _render_pixels(self, dispen):
        x = self.crtc.char_position * self.pixels_per_byte if self.pixels_per_byte else 0
        y = self.crtc.line_position

        if y >= self.height or x >= self.width:
            return  # hors du framebuffer courant (bordure hors gabarit)

        if not dispen:
            pixels = self._decode_pixels(self.memory.read_byte(self.crtc.memory_address)
                                          if self.memory else 0)
        else:
            pixels = [ColourMap[self._border_colour]] * max(self.pixels_per_byte, 1)

        for i, colour in enumerate(pixels):
            if x + i < self.width:
                self.screen[y][x + i] = colour

    def _decode_pixels(self, data):
        # Correspondances bit -> pixel telles que documentees sur
        # http://cpctech.cpcwiki.de/docs/graphics.html (portees de C#)
        if self.screen_mode == 0:
            p0 = ((data & 0x80) >> 7) | ((data & 0x08) >> 2) | ((data & 0x20) >> 3) | ((data & 0x02) << 2)
            p1 = ((data & 0x40) >> 6) | ((data & 0x04) >> 1) | ((data & 0x10) >> 2) | ((data & 0x01) << 3)
            return [ColourMap[self._pen_colours[p0]], ColourMap[self._pen_colours[p1]]]

        if self.screen_mode == 1:
            p0 = ((data & 0x08) >> 2) | ((data & 0x80) >> 7)
            p1 = ((data & 0x04) >> 1) | ((data & 0x40) >> 6)
            p2 = (data & 0x02) | ((data & 0x20) >> 5)
            p3 = ((data & 0x01) << 1) | ((data & 0x10) >> 4)
            return [ColourMap[self._pen_colours[p0]], ColourMap[self._pen_colours[p1]],
                    ColourMap[self._pen_colours[p2]], ColourMap[self._pen_colours[p3]]]

        if self.screen_mode == 2:
            return [ColourMap[self._pen_colours[(data >> (7 - i)) & 0x01]] for i in range(8)]

        return []

    # --- Etat expose au frontend ----------------------------------------

    def get_screen_buffer(self):
        return {
            "pixels": self.screen,
            "width": self.width,
            "height": self.height,
            "mode": self.screen_mode,
            "border": ColourMap[self._border_colour],
        }