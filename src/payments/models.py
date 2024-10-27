import datetime

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_key = models.CharField(max_length=255)
    order_id = models.CharField(max_length=255)
    order_name = models.CharField(max_length=255)
    method = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=255)
    amount = models.PositiveIntegerField()
    requested_at = models.DateTimeField()
    approved_at = models.DateTimeField(null=True)
