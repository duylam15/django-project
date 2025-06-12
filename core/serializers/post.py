from rest_framework import serializers
from core.models import Post
from core.serializers.post_media import PostMediaSerializer
class PostSerializer(serializers.ModelSerializer):
    media_list = PostMediaSerializer(many=True, read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'content', 'created_at', 'media_list', 'user', 'type_post', 'visibility']
