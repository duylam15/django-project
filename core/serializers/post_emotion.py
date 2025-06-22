from rest_framework import serializers
from core.models import PostEmotion

class PostEmotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostEmotion
        fields = '__all__'
        read_only_fields = ['user', 'created_at']  # 👈 để user chỉ set từ view
