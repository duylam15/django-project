from rest_framework import serializers
from core.models import Conversation
from core.serializers import UserSerializer

class ConversationSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'name', 'is_group', 'created_by', 'created_at', 'members']

    def get_members(self, obj):
        conversation_members = obj.conversationmember_set.all()
        users = [cm.user for cm in conversation_members]
        return UserSerializer(users, many=True).data
