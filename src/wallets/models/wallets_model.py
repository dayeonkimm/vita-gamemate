from django.db import models

from users.models.user_model import User


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    coin = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
