import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .emulator import get_emulator

class EmulatorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.emulator = get_emulator()
        if not self.emulator.running or not self.emulator.roms_loaded:
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
            pressed = data.get("pressed", True)
            if key:
                if pressed:
                    self.emulator.press_key(key)
                else:
                    self.emulator.release_key(key)
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

        elif event_type == "load_rom":
            firmware_path = data.get("firmware_path")
            basic_path = data.get("basic_path")
            if firmware_path and basic_path:
                try:
                    self.emulator.load_roms(firmware_path, basic_path)
                    self.emulator.roms_loaded = True
                    await self.send(text_data=json.dumps({
                        "type": "rom_loaded",
                        "success": True
                    }))
                except Exception as e:
                    await self.send(text_data=json.dumps({
                        "type": "rom_loaded",
                        "success": False,
                        "error": str(e)
                    }))

        elif event_type == "load_tape":
            filename = data.get("filename")
            tape_data = data.get("data")
            if filename and tape_data:
                try:
                    data_bytes = bytes.fromhex(tape_data)
                    self.emulator.tape.load_tape(filename, data_bytes)
                    await self.send(text_data=json.dumps({
                        "type": "tape_loaded",
                        "success": True,
                        "filename": filename
                    }))
                except Exception as e:
                    await self.send(text_data=json.dumps({
                        "type": "tape_loaded",
                        "success": False,
                        "error": str(e)
                    }))

        elif event_type == "tape_control":
            action = data.get("action")
            if action == "play":
                self.emulator.tape.play()
            elif action == "stop":
                self.emulator.tape.stop()
            elif action == "rewind":
                self.emulator.tape.rewind()
            elif action == "eject":
                self.emulator.tape.eject()
            await self.send(text_data=json.dumps({
                "type": "tape_status",
                "playing": self.emulator.tape.playing,
                "motor_on": self.emulator.tape.motor_on,
                "loaded": self.emulator.tape.loaded
            }))

    async def send_screen_loop(self):
        while self.running:
            state = self.emulator.get_screen_state()
            await self.send(text_data=json.dumps({
                "type": "screen",
                "data": state
            }))
            await asyncio.sleep(0.02)