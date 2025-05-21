from django.db import models

class ConversationMember(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
