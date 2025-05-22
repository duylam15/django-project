from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "phone_number", "password", "url_avatar", "url_background",
            "is_active", "is_online"
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        validated_data['is_active'] = True  # ✅ ép active khi đăng ký
        return User.objects.create_user(**validated_data)
