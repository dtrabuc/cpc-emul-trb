from rest_framework.views import APIView
from rest_framework.response import Response
from core.emulator import Emulator

emulator = Emulator()

class StateView(APIView):
    def get(self, request):
        return Response(emulator.get_screen_state())

class KeyPressView(APIView):
    def post(self, request):
        key = request.data.get('key')
        if key:
            # Ici, logique pour envoyer la touche à l'émulateur
            # Pour l'instant, on simule un affichage
            print(f"Touche reçue : {key}")
            return Response({'status': 'ok'})
        return Response({'error': 'Aucune touche'}, status=400)