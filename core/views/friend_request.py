from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from core.models import FriendRequest, Friend
from core.serializers import FriendRequestSerializer
from core.helper.notify import send_notify_socket 
from django.db.models import Q


class FriendRequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        send_notify_socket(instance.to_user.id, {
            "type": "friend_request",
            "message": f"{instance.from_user.username} đã gửi lời mời kết bạn.",
            "request_id": instance.id,
            "from_user_id": instance.from_user.id,  
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
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        from_user_id = request.query_params.get('from')
        to_user_id = request.query_params.get('to')

        if not from_user_id or not to_user_id:
            return Response({'detail': 'Thiếu tham số `from` hoặc `to`'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from_user_id = int(from_user_id)
            to_user_id = int(to_user_id)
        except ValueError:
            return Response({'detail': 'ID không hợp lệ'}, status=400)

        # ✅ Kiểm tra cả 2 chiều
        is_friend = Friend.objects.filter(
            Q(user_id=from_user_id, friend_id=to_user_id) |
            Q(user_id=to_user_id, friend_id=from_user_id)
        ).exists()
        if is_friend:
            return Response({'status': 'friends'})

        # Đã gửi lời mời
        sent = FriendRequest.objects.filter(from_user=from_user_id, to_user=to_user_id, accepted=False, declined=False).first()
        if sent:
            return Response({'status': 'sent', 'request_id': sent.id})

        # Đang nhận lời mời
        received = FriendRequest.objects.filter(from_user=to_user_id, to_user=from_user_id, accepted=False, declined=False).first()
        if received:
            return Response({'status': 'received', 'request_id': received.id})

        return Response({'status': 'none'})