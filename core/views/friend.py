from rest_framework import viewsets
from core.models import Friend
from core.serializers import FriendSerializer

class FriendViewSet(viewsets.ModelViewSet):
    queryset = Friend.objects.all()
    serializer_class = FriendSerializer
