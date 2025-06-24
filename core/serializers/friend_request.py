from rest_framework import serializers
from core.models import FriendRequest, Friend

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = '__all__'

    def validate(self, attrs):
        from_user = attrs.get('from_user')
        to_user = attrs.get('to_user')

        if from_user == to_user:
            raise serializers.ValidationError("Không thể gửi lời mời cho chính mình.")

        # Check đã có lời mời ngược chiều
        if FriendRequest.objects.filter(from_user=to_user, to_user=from_user).exists():
            raise serializers.ValidationError("Người này đã gửi lời mời cho bạn rồi.")

        # Check đã gửi rồi
        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            raise serializers.ValidationError("Bạn đã gửi lời mời trước đó.")

        # Check đã là bạn bè
        if Friend.objects.filter(user=from_user, friend=to_user).exists() or \
        Friend.objects.filter(user=to_user, friend=from_user).exists():
            raise serializers.ValidationError("Hai người đã là bạn bè.")

        return attrs
