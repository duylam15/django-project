from rest_framework import serializers
from core.models import Post
from core.serializers.post_media import PostMediaSerializer
class PostSerializer(serializers.ModelSerializer):
    media_list = PostMediaSerializer(many=True, read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'content', 'created_at', 'media_list', 'user', 'type_post', 'visibility','number_emotion', 'number_comment', 'number_share']
        read_only_fields = ['user']
        
    def create(self, validated_data):
            validated_data['user'] = self.context['request'].user  # 👈 Gán user từ token
            return super().create(validated_data)