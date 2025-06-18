from rest_framework import viewsets
from core.models import Comment
from core.serializers import CommentSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from core.helper.permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly, IsAuthenticatedOrReadOnly

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def get_serializer_context(self):
        return {'request': self.request}