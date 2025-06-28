from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True, db_index=True)
    email = models.EmailField(unique=True, db_index=True) 
    phone_number = models.CharField(max_length=15, blank=True, db_index=True) 
    is_active = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)
    last_active_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    avatar = models.CharField(max_length=255, blank=True, null=True) 
    url_background = models.URLField(blank=True, null=True)
    USER_ROLE = [
        ('USER', 'User'),
        ('ADMIN', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=USER_ROLE, default='USER')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
