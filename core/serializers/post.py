from rest_framework import serializers
from core.models import Post

class PostSerializer(serializers.ModelSerializer):
    def validate_content(self, value):
        if value and len(value) > 5000:
            raise serializers.ValidationError("Nội dung bài viết không được vượt quá 5000 ký tự.")
        return value

    def validate(self, data):
        if data['type_post'] == 'text' and not data.get('content'):
            raise serializers.ValidationError("Bài viết dạng văn bản phải có nội dung.")
        return data

    class Meta:
        model = Post
        fields = '__all__'
