from rest_framework import viewsets
from core.models import PostEmotion
from core.serializers import PostEmotionSerializer

class PostEmotionViewSet(viewsets.ModelViewSet):
    queryset = PostEmotion.objects.all()
    serializer_class = PostEmotionSerializer
