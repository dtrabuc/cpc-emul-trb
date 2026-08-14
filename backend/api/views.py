from rest_framework.views import APIView
from rest_framework.response import Response
from core.emulator import Emulator

emulator = Emulator()

class StateView(APIView):
    def get(self, request):
        return Response(emulator.get_screen_state())