from rest_framework import serializers
from core.models import PostMedia

class PostMediaSerializer(serializers.ModelSerializer):
    media = serializers.ImageField(use_url=True)

    class Meta:
        model = PostMedia
        fields = ['id', 'media', 'uploaded_at']