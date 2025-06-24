from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from core.models import FriendRequest, Friend
from core.serializers import FriendRequestSerializer
from core.helper.notify import send_notify_socket 


class FriendRequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        send_notify_socket(instance.to_user.id, {
            "type": "friend_request",
            "message": f"{instance.from_user.username} đã gửi lời mời kết bạn.",
            "request_id": instance.id
        })

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        fr = self.get_object()
        if fr.to_user != request.user:
            return Response({'detail': 'Không có quyền!'}, status=403)

        fr.accepted = True
        fr.save()

        # Luôn chỉ tạo 1 dòng Friend: user có ID nhỏ hơn làm user chính
        user1 = fr.from_user
        user2 = fr.to_user
        if user1.id > user2.id:
            user1, user2 = user2, user1

        if not Friend.objects.filter(user=user1, friend=user2).exists():
            Friend.objects.create(user=user1, friend=user2)


        send_notify_socket(fr.from_user.id, {
            "type": "friend_accept",
            "message": f"{fr.to_user.username} đã chấp nhận lời mời kết bạn!"
        })

        return Response({'detail': 'Đã chấp nhận kết bạn.'})


    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        fr = self.get_object()
        if fr.to_user != request.user:
            return Response({'detail': 'Không có quyền!'}, status=403)

        send_notify_socket(fr.from_user.id, {
            "type": "friend_decline",
            "message": f"{fr.to_user.username} đã từ chối lời mời kết bạn!"
        })

        fr.delete()  # xoá khỏi DB luôn
        return Response({'detail': 'Đã từ chối và xoá lời mời kết bạn.'})
