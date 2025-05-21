from rest_framework import viewsets
from core.models import Conversation
from core.serializers import ConversationSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
