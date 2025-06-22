from rest_framework import viewsets
from core.models import User
from core.serializers import UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from core.helper.permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly, IsAuthenticatedOrReadOnly

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def get_permissions(self):
            if self.action in ['list', 'retrieve']:
                return [AllowAny()]
            return [IsAuthenticated()]