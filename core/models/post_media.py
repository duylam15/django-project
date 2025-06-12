from django.db import models

class PostMedia(models.Model):
    post = models.ForeignKey('Post', related_name='media_list', on_delete=models.CASCADE)
    media = models.ImageField(upload_to='post_media/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Media for Post {self.post.id}"
