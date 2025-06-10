from django.db import models

class Friend(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='friends')
    friend = models.ForeignKey('User', on_delete=models.CASCADE, related_name='friend_of')
    created_at = models.DateTimeField(auto_now_add=True)
    userBlockFriend = models.BooleanField(default=False)
    friendBlockUser = models.BooleanField(default=False)	