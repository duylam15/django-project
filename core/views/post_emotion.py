from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.models import PostEmotion, Post
from core.serializers import PostEmotionSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import models

class PostEmotionViewSet(viewsets.ModelViewSet):
    queryset = PostEmotion.objects.all()
    serializer_class = PostEmotionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        post_id = request.data.get('post')
        user = request.user

        # ✅ Check đã like chưa
        if PostEmotion.objects.filter(post_id=post_id, user=user).exists():
            return Response({'detail': 'Bạn đã like bài viết này rồi.'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Tạo like mới
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)

        # ✅ Tăng số lượng like của post
        Post.objects.filter(id=post_id).update(number_emotion=models.F('number_emotion') + 1)

        # ✅ Gửi thông báo realtime
        post = Post.objects.get(id=post_id)
        if post.user != user:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"notify_user_{post.user.id}",
                {
                    "type": "send_notification",
                    "content": {
                        "type": "like_post",
                        "message": f"{user.username} đã thích bài viết của bạn.",
                        "post_id": post.id,
                        "user_send_id": user.id,
                        "user_receive_id": post.user.id,
                    },
                }
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        post = instance.post

        # ✅ Xóa like
        self.perform_destroy(instance)

        # ✅ Giảm số lượng like
        Post.objects.filter(id=post.id).update(number_emotion=models.F('number_emotion') - 1)

        return Response(status=status.HTTP_204_NO_CONTENT)
