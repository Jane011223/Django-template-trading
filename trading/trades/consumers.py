from channels.generic.websocket import AsyncWebsocketConsumer

class StreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('stream', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('stream', self.channel_name)

    async def stream_message(self, event):
        message = event['message']
        await self.send(message)