import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .emulator import Emulator

class EmulatorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.emulator = Emulator()
        self.emulator.reset()
        await self.accept()
        # Envoyer l'état initial
        await self.send_screen()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'key':
            key = data.get('key')
            # Envoyer la touche à l'émulateur (à implémenter)
            self.emulator.send_key(key)
            # Exécuter quelques cycles CPU
            for _ in range(1000):
                self.emulator.step()
            await self.send_screen()

    async def send_screen(self):
        state = self.emulator.get_screen_state()
        await self.send(text_data=json.dumps({
            'type': 'screen',
            'data': state
        }))