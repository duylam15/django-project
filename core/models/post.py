from django.db import models

class Post(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    content = models.TextField(max_length=5000)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    number_emotion = models.IntegerField(default=0)
    number_comment = models.IntegerField(default=0)
    number_share = models.IntegerField(default=0)
    
    POST_VISIBILITY_CHOICES = [
        ('PUBLIC', 'Public'),
        ('FRIENDS', 'Friends'),
        ('PRIVATE', 'Private'),
    ]
    visibility = models.CharField(max_length=20, choices=POST_VISIBILITY_CHOICES, default='PUBLIC')

    POST_TYPE_CHOICES = [
        ('TEXT', 'Text'),
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
    ]
    type_post = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, default='TEXT')
