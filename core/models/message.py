from django.db import models

class Message(models.Model):
    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE)
    sender = models.ForeignKey('User', on_delete=models.CASCADE)
    content = models.TextField()
    MEDIA_TYPE_CHOICES = [
        ('TEXT', 'Text'),
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
    ]
    type_message = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES, default='TEXT')
    update_at = models.DateTimeField(auto_now=True)
