import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificacionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.restaurante_id = self.scope["url_route"]["kwargs"]["restaurante_id"]
        self.room_group_name = f"notificaciones_{self.restaurante_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "notificacion_message", "message": data}
        )

    async def notificacion_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))
