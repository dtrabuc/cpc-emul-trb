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
        print(f"[BACKEND] Touche reçue : {key}")
        # Simuler un affichage de la touche sur l'écran
        screen = emulator.gate_array.screen
        cursor_x = emulator.gate_array.cursor_x
        cursor_y = emulator.gate_array.cursor_y
        
        if key == 'ENTER':
            # On passe à la ligne
            emulator.gate_array.cursor_x = 0
            emulator.gate_array.cursor_y += 1
        elif key == 'DEL' or key == 'Backspace':
            # Effacer le caractère précédent
            if cursor_x > 0:
                emulator.gate_array.cursor_x -= 1
                screen[cursor_y][cursor_x - 1] = ' '
        elif key == 'SPACE':
            screen[cursor_y][cursor_x] = ' '
            emulator.gate_array.cursor_x += 1
        elif len(key) == 1:
            # Touche alphanumérique
            screen[cursor_y][cursor_x] = key
            emulator.gate_array.cursor_x += 1
        
        # Si on dépasse 80 colonnes, on passe à la ligne
        if emulator.gate_array.cursor_x >= 80:
            emulator.gate_array.cursor_x = 0
            emulator.gate_array.cursor_y += 1
        
        return Response({'status': 'ok', 'key': key})

class ResetView(APIView):
    def post(self, request):
        emulator.reset()
        return Response({'status': 'reset_ok'})