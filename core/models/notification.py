from django.db import models

class Notification(models.Model):
    receiver = models.ForeignKey('User', on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey('User', on_delete=models.CASCADE, related_name='sent_notifications')
    type = models.CharField(max_length=50)
    post_id = models.IntegerField(null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
