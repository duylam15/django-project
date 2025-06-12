from rest_framework import viewsets
from core.models import Message
from core.serializers import MessageSerializer
from rest_framework.permissions import IsAuthenticated

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)