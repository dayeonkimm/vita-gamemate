from rest_framework import serializers

from .models import Payment


class PaymentCreateSerializer(serializers.Serializer):
    payment_key = serializers.CharField()
    order_id = serializers.CharField()
    amount = serializers.IntegerField()


class PaymentSerializer(serializers.ModelSerializer):

    user_nickname = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ["user_nickname", "payment_key", "order_id", "order_name", "method", "status", "amount", "requested_at", "approved_at"]

    def get_user_nickname(self, obj):
        return obj.user.nickname
