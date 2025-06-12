from django.db import models
class Message(models.Model):
    TEXT = 'text'
    IMAGE = 'image'
    VIDEO = 'video'
    MESSAGE_TYPES = [
        (TEXT, 'Text'),
        (IMAGE, 'Image'),
        (VIDEO, 'Video'),
    ]

    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('User', on_delete=models.CASCADE)
    type_message = models.CharField(max_length=10, choices=MESSAGE_TYPES, default=TEXT)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
