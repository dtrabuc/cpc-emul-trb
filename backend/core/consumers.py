# core/consumers.py
import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer

class EmulatorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
            
        data = json.loads(text_data)
        event_type = data.get("type")

        # Gestion Clavier
        if event_type == "KEY_DOWN":
            self.emulator.keyboard.key_down(data.get("key"))
        elif event_type == "KEY_UP":
            self.emulator.keyboard.key_up(data.get("key"))

        # Gestion Datacorder Cassette
        elif event_type == "TAPE_LOAD":
            raw_file = base64.b64decode(data.get("payload"))
            filename = data.get("filename", "tape.cdt")
            self.emulator.tape.load_tape(filename, raw_file)
            await self.send_tape_status()

        elif event_type == "TAPE_CONTROL":
            action = data.get("action")
            if action == "PLAY":
                self.emulator.tape.play()
            elif action == "STOP":
                self.emulator.tape.stop()
            elif action == "REWIND":
                self.emulator.tape.rewind()
            elif action == "EJECT":
                self.emulator.tape.eject()
            await self.send_tape_status()

    async def send_tape_status(self):
        tape = self.emulator.tape
        await self.send(json.dumps({
            "type": "TAPE_STATUS",
            "loaded": tape.loaded,
            "filename": tape.filename,
            "playing": tape.playing,
            "counter": tape.counter
        }))