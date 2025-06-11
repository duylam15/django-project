from rest_framework import serializers
from core.models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
        
    # def create(self, validated_data):
    #     print("Media in validated_data:", validated_data.get("media"))
    #     return super().create(validated_data)
