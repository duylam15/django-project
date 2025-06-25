from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from core.models import Friend, User
from core.serializers import FriendSerializer
from rest_framework import status
from django.db.models import Q
from rest_framework.decorators import api_view

class FriendViewSet(viewsets.ModelViewSet):
    queryset = Friend.objects.all()
    serializer_class = FriendSerializer
    pagination_class = None

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def list_friends(self, request, user_id=None):
        user = get_object_or_404(User, pk=user_id)
        friends = Friend.objects.filter(user=user) | Friend.objects.filter(friend=user)
        serializer = self.get_serializer(friends, many=True, context={"request_user_id": user.id})
        return Response(serializer.data)


    @action(detail=False, methods=['get'], url_path='check')
    def check_friendship(self, request):
        user1_id = request.query_params.get('user1')
        user2_id = request.query_params.get('user2')

        if not user1_id or not user2_id:
            return Response(
                {'detail': 'Thiếu tham số user1 hoặc user2.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user1_id = int(user1_id)
            user2_id = int(user2_id)
        except ValueError:
            return Response({'detail': 'ID phải là số nguyên.'}, status=400)

        is_friend = Friend.objects.filter(
            Q(user_id=user1_id, friend_id=user2_id) |
            Q(user_id=user2_id, friend_id=user1_id),
            userBlockFriend=False,
            friendBlockUser=False
        ).exists()

        return Response({'are_friends': is_friend})
        user1_id = request.query_params.get('user1')
        user2_id = request.query_params.get('user2')

        # Kiểm tra thiếu tham số
        if not user1_id or not user2_id:
            return Response(
                {'detail': 'Thiếu tham số user1 hoặc user2.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user1_id = int(user1_id)
            user2_id = int(user2_id)
        except ValueError:
            return Response({'detail': 'ID phải là số nguyên.'}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra quan hệ bạn bè 2 chiều và không bị block
        is_friend = Friend.objects.filter(
            Q(user_id=user1_id, friend_id=user2_id) |
            Q(user_id=user2_id, friend_id=user1_id),
            userBlockFriend=False,
            friendBlockUser=False
        ).exists()

        return Response({'are_friends': is_friend}, status=status.HTTP_200_OK)