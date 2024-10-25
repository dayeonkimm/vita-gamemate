from django.contrib.auth import get_user_model
from django.db import models
import datetime

User = get_user_model()


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_key = models.CharField(max_length=255)
    order_id = models.CharField(max_length=255)
    order_name = models.CharField(max_length=255, default="unknown")
    method = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=255,default="unknown")
    amount = models.PositiveIntegerField()
    requested_at = models.DateTimeField(default=datetime.datetime.now)
    approved_at = models.DateTimeField(null=True)
    
