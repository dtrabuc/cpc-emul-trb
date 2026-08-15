from django.db import models

class ROM(models.Model):
    TYPE_CHOICES = [
        ('BASIC', 'BASIC 1.0'),
        ('FIRMWARE', 'Firmware'),
        ('EXTENSION', 'Extension ROM'),
    ]
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    file = models.FileField(upload_to='roms/')
    size = models.IntegerField()
    checksum = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.name

class Tape(models.Model):
    FORMAT_CHOICES = [('TAP', 'TAP'), ('CDT', 'CDT')]
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='tapes/')
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class EmulatorState(models.Model):
    name = models.CharField(max_length=50, default="Autosave")
    created_at = models.DateTimeField(auto_now_add=True)

    # CPU registers
    pc = models.IntegerField(default=0x0000)
    sp = models.IntegerField(default=0xFFFF)
    af = models.IntegerField(default=0x0000)
    bc = models.IntegerField(default=0x0000)
    de = models.IntegerField(default=0x0000)
    hl = models.IntegerField(default=0x0000)
    af_alt = models.IntegerField(default=0x0000)
    bc_alt = models.IntegerField(default=0x0000)
    de_alt = models.IntegerField(default=0x0000)
    hl_alt = models.IntegerField(default=0x0000)
    ix = models.IntegerField(default=0x0000)
    iy = models.IntegerField(default=0x0000)
    i = models.IntegerField(default=0x00)
    r = models.IntegerField(default=0x00)
    iff1 = models.BooleanField(default=False)
    iff2 = models.BooleanField(default=False)

    ram = models.BinaryField()
    crtc_regs = models.JSONField(default=dict)
    ay_regs = models.JSONField(default=dict)
    pio_regs = models.JSONField(default=dict)
    screen_buffer = models.JSONField(default=list)
    cursor_x = models.IntegerField(default=0)
    cursor_y = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.created_at}"