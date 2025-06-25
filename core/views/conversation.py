from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import Conversation, User, ConversationMember
from core.serializers import ConversationSerializer, ConversationMemberSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        conversation = self.get_object()
        user_id = request.data.get("user_id")
        user = User.objects.get(id=user_id)
        member = ConversationMember.objects.create(user=user, conversation=conversation)
        return Response(ConversationMemberSerializer(member).data)

    # ✅ Đây là action đúng cách để lấy conversation theo user_id
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def conversations_by_user(self, request, user_id=None):
        memberships = ConversationMember.objects.filter(user_id=user_id)
        conversation_ids = memberships.values_list('conversation_id', flat=True)
        conversations = Conversation.objects.filter(id__in=conversation_ids).distinct()
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
