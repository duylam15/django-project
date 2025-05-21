from rest_framework import serializers
from core.models import ConversationMember

class ConversationMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationMember
        fields = '__all__'
