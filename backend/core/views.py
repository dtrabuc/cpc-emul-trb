from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.emulator import Emulator
from core.models import EmulatorState, ROM, Tape
from .serializers import StateSerializer, KeyPressSerializer

# Instance globale de l'émulateur (à gérer avec soin)
emulator = Emulator()

class StateView(APIView):
    """Retourne l'état actuel de l'émulateur (écran + registres)"""
    def get(self, request):
        return Response({
            'screen': emulator.get_screen_buffer(),
            'cursor_x': emulator.cursor_x,
            'cursor_y': emulator.cursor_y,
            'status': emulator.status,  # 'running', 'paused', 'error'
            'mode': emulator.video_mode,  # 0, 1, 2
        })

class KeyPressView(APIView):
    """Envoie une touche à l'émulateur"""
    def post(self, request):
        serializer = KeyPressSerializer(data=request.data)
        if serializer.is_valid():
            key = serializer.validated_data['key']
            # Convertir la touche en scancode CPC
            scancode = emulator.keyboard_map.get(key, 0x00)
            emulator.press_key(scancode)
            # Exécuter quelques cycles pour traiter la touche
            emulator.run_cycles(1000)
            return Response({'status': 'ok'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetView(APIView):
    """Réinitialise l'émulateur"""
    def post(self, request):
        emulator.reset()
        return Response({'status': 'reset_ok'})

class LoadROMView(APIView):
    """Charge une ROM (BASIC ou Firmware)"""
    def post(self, request):
        rom_id = request.data.get('rom_id')
        try:
            rom = ROM.objects.get(id=rom_id)
            emulator.load_rom(rom.file.path, rom.type)
            return Response({'status': 'ok', 'rom': rom.name})
        except ROM.DoesNotExist:
            return Response({'error': 'ROM not found'}, status=404)

class LoadTapeView(APIView):
    """Charge un programme cassette"""
    def post(self, request):
        tape_id = request.data.get('tape_id')
        try:
            tape = Tape.objects.get(id=tape_id)
            emulator.load_tape(tape.file.path)
            return Response({'status': 'ok', 'tape': tape.name})
        except Tape.DoesNotExist:
            return Response({'error': 'Tape not found'}, status=404)

class SaveStateView(APIView):
    """Sauvegarde l'état actuel"""
    def post(self, request):
        state = EmulatorState.objects.create(
            name=request.data.get('name', 'Autosave'),
            pc=emulator.pc,
            sp=emulator.sp,
            # ... tous les registres
            ram=emulator.get_ram_binary(),
            screen_buffer=emulator.get_screen_buffer(),
        )
        return Response({'id': state.id, 'name': state.name})

class LoadStateView(APIView):
    """Charge un état sauvegardé"""
    def post(self, request):
        state_id = request.data.get('state_id')
        try:
            state = EmulatorState.objects.get(id=state_id)
            emulator.restore_state(state)
            return Response({'status': 'ok'})
        except EmulatorState.DoesNotExist:
            return Response({'error': 'State not found'}, status=404)