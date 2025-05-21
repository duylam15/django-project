from rest_framework import viewsets
from core.models import ConversationMember
from core.serializers import ConversationMemberSerializer

class ConversationMemberViewSet(viewsets.ModelViewSet):
    queryset = ConversationMember.objects.all()
    serializer_class = ConversationMemberSerializer
