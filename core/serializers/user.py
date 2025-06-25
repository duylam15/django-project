from rest_framework import serializers
from django.conf import settings
from core.models import User


class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "phone_number", "password", "avatar","avatar_url", "url_background",
            "is_active", "is_online", "role"
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }
        
    def get_avatar_url(self, obj):
            if obj.avatar:
                return f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{obj.avatar}"
            return None