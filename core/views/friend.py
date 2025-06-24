from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from core.models import Friend, User
from core.serializers import FriendSerializer

class FriendViewSet(viewsets.ModelViewSet):
    queryset = Friend.objects.all()
    serializer_class = FriendSerializer

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def list_friends(self, request, user_id=None):
        user = get_object_or_404(User, pk=user_id)
        friends = Friend.objects.filter(user=user) | Friend.objects.filter(friend=user)
        serializer = self.get_serializer(friends, many=True, context={"request_user_id": user.id})
        return Response(serializer.data)

