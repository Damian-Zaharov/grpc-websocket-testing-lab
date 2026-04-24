import asyncio
import json
import websockets

class TickerWsClient:
    def __init__(self, url="ws://ticker-service:8765"):
        self.url = url
        self.connection = None

    async def connect(self):
        self.connection = await websockets.connect(self.url)

    async def disconnect(self):
        if self.connection:
            await self.connection.close()

    async def listen(self, count=3, timeout=5):
        """Читает ровно count сообщений"""
        messages = []
        for _ in range(count):
            try:
                msg = await asyncio.wait_for(self.connection.recv(), timeout=timeout)
                messages.append(json.loads(msg))
            except asyncio.TimeoutError:
                break
        return messages

