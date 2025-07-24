from django.db import models

# class Comment(models.Model):
#     post = models.ForeignKey('Post', on_delete=models.CASCADE)
#     user = models.ForeignKey('User', on_delete=models.CASCADE)
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     number_emotion = models.IntegerField(default=0)
#     number_comment_child = models.IntegerField(default=0)

#     COMMENT_TYPE_CHOICES = [
#         ('NORMAL', 'Normal'),
#         ('GIF', 'GIF'),
#         ('MEDIA', 'Media'),
#     ]
#     type_comment = models.CharField(max_length=20, choices=COMMENT_TYPE_CHOICES, default='NORMAL')

#     parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
