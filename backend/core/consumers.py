# core/consumers.py
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .emulator import Emulator

class EmulatorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.emulator = Emulator()
        self.emulator.reset()
        self.running = True
        await self.accept()
        asyncio.create_task(self.send_screen_loop())

    async def disconnect(self, close_code):
        self.running = False
        self.emulator.running = False

    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get("type")

        if event_type == "key":
            key = data.get("key")
            if key:
                self.emulator.press_key(key)
                self.emulator.dispatch_cycles(1000)

        elif event_type == "cycles":
            count = data.get("count", 16000)
            self.emulator.dispatch_cycles(count)

        elif event_type == "reset":
            self.emulator.reset()

        elif event_type == "get_status":
            status = self.emulator.get_status()
            await self.send(text_data=json.dumps({
                "type": "status",
                "data": status
            }))

    async def send_screen_loop(self):
        while self.running:
            state = self.emulator.get_screen_state()
            await self.send(text_data=json.dumps({
                "type": "screen",
                "data": state
            }))
            await asyncio.sleep(0.02)  # 50 FPS