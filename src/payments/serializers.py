from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    
    user_nickname = serializers.SerializerMethodField()
    
    order_name = serializers.CharField(max_length=255, required=False, write_only=True)
    method = serializers.CharField(max_length=255, required=False, write_only=True)
    status = serializers.CharField(max_length=255, required=False, write_only=True)
    requested_at = serializers.DateTimeField(required=False, write_only=True)
    approved_at = serializers.DateTimeField(required=False, write_only=True)

    class Meta:
        model = Payment
        fields = ["user_nickname", "payment_key", "order_id", "order_name", "method", "status", "amount", "requested_at", "approved_at"]
        
    def get_user_nickname(self, obj):
        return obj.user.nickname
