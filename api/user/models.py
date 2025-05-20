from django.db import models

class User(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)

    def __str__(self):
        return self.title
