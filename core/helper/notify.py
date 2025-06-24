# core/helper/notify.py
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_notify_socket(user_id, data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notify_user_{user_id}",
        {
            "type": "send_notification",
            "content": data
        }
    )
