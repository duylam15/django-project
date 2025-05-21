from rest_framework import serializers
from core.models import PostEmotion

class PostEmotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostEmotion
        fields = '__all__'
