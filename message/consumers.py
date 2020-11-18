import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.auth import login

class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_group_name = "message"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        username = text_data_json["username"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "host": self.user.username,
                "guest": username
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        host = event["host"]
        guest = event["guest"]
        if guest == self.user.username or host == self.user.username:
            await self.send(text_data=json.dumps({"host": host, "guest": guest}))