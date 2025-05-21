from django.contrib.auth.models import AbstractUser
from django.db import models

class Conversation(models.Model):
    name = models.CharField(max_length=255)
    is_group = models.BooleanField(default=False)
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='created_conversations')
    created_at = models.DateTimeField(auto_now_add=True)

