import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        print(f"[CONNECT] Client joined room: {self.room_group_name}")
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        print(f"[DISCONNECT] Client left room: {self.room_group_name} (code {close_code})")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message', '')

            print(f"[RECEIVE] Message from client: {message}")

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message
                }
            )
        except Exception as e:
            print(f"[ERROR] Failed to receive message: {e}")

    async def chat_message(self, event):
        message = event['message']
        print(f"[SEND] Broadcasting message: {message}")

        await self.send(text_data=json.dumps({
            'message': message
        }))


# core/helper/consumer.py
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.group_name = f"notify_user_{self.user_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print(f"[WS] Connected to notify group: {self.group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print(f"[WS] Disconnected: {self.group_name}")

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event["content"]))
