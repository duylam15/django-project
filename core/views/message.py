from rest_framework import viewsets
from core.models import Message
from core.serializers import MessageSerializer

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by('-update_at')
    serializer_class = MessageSerializer
