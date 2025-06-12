from rest_framework import viewsets
from core.models import Conversation
from core.models import User
from core.models import ConversationMember
from core.serializers import ConversationMemberSerializer
from core.serializers import ConversationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        conversation = self.get_object()
        user_id = request.data.get("user_id")
        user = User.objects.get(id=user_id)
        member = ConversationMember.objects.create(user=user, conversation=conversation)
        return Response(ConversationMemberSerializer(member).data)
