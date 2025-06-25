from rest_framework import viewsets
from core.models import ConversationMember
from core.serializers import ConversationMemberSerializer,ConversationSerializer
from rest_framework import status
from rest_framework.response import Response
from core.models import ConversationMember, Conversation

class ConversationMemberViewSet(viewsets.ModelViewSet):
    queryset = ConversationMember.objects.all()
    serializer_class = ConversationMemberSerializer

