# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from core.emulator import Emulator

emulator = Emulator()

class StateView(APIView):
    def get(self, request):
        return Response(emulator.get_screen_state())

class KeyPressView(APIView):
    def post(self, request):
        key = request.data.get('key')
        if key:
            emulator.press_key(key)
            emulator.dispatch_cycles(1000)
            return Response({'status': 'ok'})
        return Response({'error': 'No key'}, status=400)

class ResetView(APIView):
    def post(self, request):
        emulator.reset()
        return Response({'status': 'reset_ok'})

class LoadROMView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        firmware = request.FILES.get('firmware')
        basic = request.FILES.get('basic')

        if not firmware or not basic:
            return Response({'error': 'Les deux fichiers ROM sont requis'}, status=400)

        firmware_path = f'roms/{firmware.name}'
        basic_path = f'roms/{basic.name}'

        with open(firmware_path, 'wb+') as f:
            for chunk in firmware.chunks():
                f.write(chunk)

        with open(basic_path, 'wb+') as f:
            for chunk in basic.chunks():
                f.write(chunk)

        emulator.load_roms(firmware_path, basic_path)
        emulator.reset()

        return Response({'status': 'ok', 'firmware': firmware.name, 'basic': basic.name})