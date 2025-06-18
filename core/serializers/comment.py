from rest_framework import serializers
from core.models import Comment

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['user']
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request_user = self.context['request'].user
        if instance.user != request_user:
            raise serializers.ValidationError("Bạn không có quyền sửa comment này.")
        validated_data.pop('user', None)  # Chặn override user
        return super().update(instance, validated_data)
