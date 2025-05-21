from rest_framework import serializers
from core.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'email', 'phone_number', 'url_avatar', 'url_background',
            'is_active', 'is_online', 'last_active_at', 'date_joined'
        ]
