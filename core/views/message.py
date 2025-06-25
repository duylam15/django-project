from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.models import Message, Notification, ConversationMember
from core.serializers import MessageSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.decorators import action
from rest_framework.response import Response

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # ← Tắt phân trang chỉ ở view này

    def perform_create(self, serializer):
        message = serializer.save(sender=self.request.user)
        channel_layer = get_channel_layer()
        conversation = message.conversation

        members = ConversationMember.objects.filter(conversation=conversation).exclude(user=self.request.user)
        
        for member in members:
            # Gửi thông báo realtime
            async_to_sync(channel_layer.group_send)(
                f"notify_user_{member.user.id}",
                {
                    "type": "send_notification",
                    "content": {
                        "type": "new_message",
                        "message": f"{self.request.user.username} đã gửi tin nhắn mới.",
                        "conversation_id": conversation.id,
                        "message_id": message.id,
                        "sender_id": self.request.user.id,
                        "content": message.content,
                    }
                }
            )

            # Lưu vào bảng Notification
            Notification.objects.create(
                receiver=member.user,
                sender=self.request.user,
                type="new_message",
                content=f"{self.request.user.username} đã gửi tin nhắn mới.",
            )

    def perform_update(self, serializer):
        message = serializer.save()
        channel_layer = get_channel_layer()
        conversation = message.conversation

        members = ConversationMember.objects.filter(conversation=conversation).exclude(user=self.request.user)

        for member in members:
            async_to_sync(channel_layer.group_send)(
                f"notify_user_{member.user.id}",
                {
                    "type": "send_notification",
                    "content": {
                        "type": "update_message",
                        "message": f"{self.request.user.username} đã cập nhật tin nhắn.",
                        "conversation_id": conversation.id,
                        "message_id": message.id,
                        "content": message.content,
                    }
                }
            )

            Notification.objects.create(
                receiver=member.user,
                sender=self.request.user,
                type="update_message",
                content=f"{self.request.user.username} đã chỉnh sửa một tin nhắn.",
            )

    def perform_destroy(self, instance):
        conversation = instance.conversation
        message_id = instance.id
        instance.delete()

        channel_layer = get_channel_layer()
        members = ConversationMember.objects.filter(conversation=conversation).exclude(user=self.request.user)

        for member in members:
            async_to_sync(channel_layer.group_send)(
                f"notify_user_{member.user.id}",
                {
                    "type": "send_notification",
                    "content": {
                        "type": "delete_message",
                        "message": f"{self.request.user.username} đã xóa một tin nhắn.",
                        "conversation_id": conversation.id,
                        "message_id": message_id,
                    }
                }
            )

            Notification.objects.create(
                receiver=member.user,
                sender=self.request.user,
                type="delete_message",
                content=f"{self.request.user.username} đã xóa một tin nhắn.",
            )

    @action(detail=False, methods=['get'], url_path='by-conversation/(?P<conversation_id>[^/.]+)')
    def by_conversation(self, request, conversation_id=None):
        messages = Message.objects.filter(conversation_id=conversation_id).order_by("updated_at")
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)