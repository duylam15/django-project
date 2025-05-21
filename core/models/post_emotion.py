from django.db import models

class PostEmotion(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    emotion = models.CharField(max_length=20)  
    created_at = models.DateTimeField(auto_now_add=True)
