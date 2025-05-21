from django.db import models

class Friend(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='friends')
    friend = models.ForeignKey('User', on_delete=models.CASCADE, related_name='friend_of')
    created_at = models.DateTimeField(auto_now_add=True)
    is_block = models.BooleanField(default=False)
    block_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='blocked_friends')
