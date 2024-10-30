from rest_framework import serializers

from wallets.models import Wallet


class WalletRechargeSerializer(serializers.Serializer):
    coin = serializers.IntegerField(required=True)

    def validate(self, attrs):
        coin_amount = attrs.get("coin")

        if coin_amount <= 0:
            raise serializers.ValidationError({"coin": "충전할 코인 양은 1 이상이어야 합니다."})

        return attrs


class WalletWithdrawSerializer(serializers.Serializer):
    coin = serializers.IntegerField(required=True)

    def validate(self, attrs):
        coin_amount = attrs.get("coin")
        wallet = self.context.get("wallet")

        # 차감할 코인 양이 유효한지 확인
        if coin_amount <= 0:
            raise serializers.ValidationError({"coin": "차감할 코인 양은 1 이상이어야 합니다."})

        # 지갑 잔액이 충분한지 확인
        if wallet and wallet.coin < coin_amount:
            raise serializers.ValidationError({"coin": "잔액이 부족합니다."})

        return attrs
