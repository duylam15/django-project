from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.models import Comment, Post
from core.serializers import CommentSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from core.helper.permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly, IsAuthenticatedOrReadOnly

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def perform_create(self, serializer):
        comment = serializer.save(user=self.request.user)
        post = comment.post
        parent = comment.parent
        channel_layer = get_channel_layer()
        
         # ✅ Tăng số lượng comment bài post
        post.number_comment += 1
        post.save(update_fields=["number_comment"])

        # 🔔 Trường hợp bình luận vào bài post của người khác → gửi cho chủ post
        if post.user != self.request.user:
            async_to_sync(channel_layer.group_send)(
                f"notify_user_{post.user.id}",
                {
                    "type": "send_notification",
                    "content": {
                        "type": "new_comment",
                        "message": f"{self.request.user.username} đã bình luận bài viết của bạn!",
                        "post_id": post.id,
                        "comment_id": comment.id,
                        "user_send_id": self.request.user.id,
                        "user_receive_id": post.user.id,
                    },
                }
            )

        # 🔔 Trường hợp bình luận vào comment của người khác → gửi cho chủ comment
        if parent and parent.user != self.request.user:
            async_to_sync(channel_layer.group_send)(
                f"notify_user_{parent.user.id}",
                {
                    "type": "send_notification",
                    "content": {
                        "type": "reply_comment",
                        "message": f"{self.request.user.username} đã trả lời bình luận của bạn!",
                        "post_id": post.id,
                        "comment_id": comment.id,
                        "parent_id": parent.id,
                        "user_send_id": self.request.user.id,
                        "user_receive_id": parent.user.id,
                    },
                }
            )
            
    def perform_update(self, serializer):
        comment = serializer.save()
        post = comment.post
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notify_user_{post.user.id}",
            {
                "type": "send_notification",
                "content": {
                    "type": "update_comment",
                    "message": f"{self.request.user.username} đã chỉnh sửa bình luận.",
                    "post_id": post.id,
                    "comment_id": comment.id,
                    "content": comment.content,
                },
            }
        )

    def perform_destroy(self, instance):
        post = instance.post
        comment_id = instance.id
        
        # ✅ Giảm số lượng comment (nếu lớn hơn 0)
        if post.number_comment > 0:
            post.number_comment -= 1
            post.save(update_fields=["number_comment"])

        instance.delete()
        
        instance.delete()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notify_user_{post.user.id}",
            {
                "type": "send_notification",
                "content": {
                    "type": "delete_comment",
                    "message": f"{self.request.user.username} đã xóa bình luận.",
                    "post_id": post.id,
                    "comment_id": comment_id,
                },
            }
        )
