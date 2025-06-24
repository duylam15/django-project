from rest_framework import serializers
from core.models import Friend, User
class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'url_avatar', 'url_background', 'is_online', 'role']

class FriendSerializer(serializers.ModelSerializer):
    friend_detail = serializers.SerializerMethodField()

    class Meta:
        model = Friend
        fields = ['id', 'created_at', 'userBlockFriend', 'friendBlockUser', 'user', 'friend','friend_detail'] 
    def get_friend_detail(self, obj):
        request_user_id = self.context.get("request_user_id")
        if obj.user.id == request_user_id:
            return UserSimpleSerializer(obj.friend).data
        else:
            return UserSimpleSerializer(obj.user).data
