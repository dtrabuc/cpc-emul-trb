from django.core.management.base import BaseCommand
from core.models import ROM

class Command(BaseCommand):
    help = 'Charge les ROMs initiales'

    def handle(self, *args, **options):
        # Créer les entrées pour les ROMs
        # À adapter selon le chemin de tes fichiers
        ROM.objects.get_or_create(
            name='CPC464 Firmware FR v1.0',
            type='FIRMWARE',
            defaults={'file': 'roms/cpc464_fr.rom', 'size': 16384}
        )
        ROM.objects.get_or_create(
            name='Locomotive BASIC 1.0',
            type='BASIC',
            defaults={'file': 'roms/basic_1.0.rom', 'size': 16384}
        )
        self.stdout.write(self.style.SUCCESS('ROMs chargées'))