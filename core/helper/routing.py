# core/helper/routing.py
from django.urls import re_path
from .consumer import ChatConsumer, NotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/notify/(?P<user_id>\d+)/$', NotificationConsumer.as_asgi()),  # ✅ thêm dòng này
]
