from django.db.models import F
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.exceptions import (
    InvalidAuthorizationHeader,
    MissingAuthorizationHeader,
    TokenMissing,
    UserNotFound,
)
from users.models import User
from users.services.user_service import UserService
from wallets.models.wallets_model import Wallet
from wallets.serializers.wallets_serializers import (
    WalletRechargeSerializer,
    WalletWithdrawSerializer,
)


class WalletBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="지갑 잔액 조회",
        description="사용자의 지갑에 있는 현재 코인 잔액을 조회하는 API입니다.",
        parameters=[
            OpenApiParameter(name="user_id", description="사용자 ID (유저 PK)", required=True, type=int, location=OpenApiParameter.PATH),
        ],
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {"user_id": {"type": "integer", "example": 1}, "coin_balance": {"type": "integer", "example": 100}},
                },
                description="Successful Balance Query",
            ),
            404: OpenApiResponse(
                response={"type": "object", "properties": {"error": {"type": "string", "example": "지갑을 찾을 수 없습니다."}}},
                description="Wallet Not Found",
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        user = request.user

        wallet = Wallet.objects.filter(user_id=user.id).first()
        if not wallet:
            return Response({"error": "지갑을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"user_id": user.id, "coin": wallet.coin}, status=status.HTTP_200_OK)


class WalletRechargeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WalletRechargeSerializer

    @extend_schema(
        summary="지갑 코인 충전",
        description="사용자의 지갑에 코인을 충전하는 API입니다. 요청 body에 충전할 코인 수를 전달해야 합니다.",
        request=WalletRechargeSerializer,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "example": "코인이 성공적으로 충전되었습니다."},
                        "coin": {"type": "integer", "example": 150},
                    },
                },
                description="Successful Coin Recharge",
            ),
            404: OpenApiResponse(
                response={"type": "object", "properties": {"error": {"type": "string", "example": "지갑을 찾을 수 없습니다."}}},
                description="Wallet Not Found",
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        user = request.user

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        coin_amount = serializer.validated_data["coin"]

        wallet = Wallet.objects.filter(user_id=user.id).first()
        if not wallet:
            return Response({"error": "지갑을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # F expression을 사용하여 동시성 문제 해결
        wallet.coin = F("coin") + coin_amount
        wallet.save()

        # 다시 데이터베이스에서 값 가져오기
        wallet.refresh_from_db()

        return Response({"message": "코인이 성공적으로 충전되었습니다.", "coin": wallet.coin}, status=status.HTTP_200_OK)


class WalletWithdrawView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WalletWithdrawSerializer

    def post(self, request, *args, **kwargs):
        user = request.user

        # 차감 시 Wallet 정보를 context로 전달
        wallet = Wallet.objects.filter(user_id=user.id).first()
        if not wallet:
            return Response({"error": "지갑을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data, context={"wallet": wallet})
        serializer.is_valid(raise_exception=True)
        coin_amount = serializer.validated_data["coin"]

        if wallet.coin < coin_amount:
            return Response({"error": "잔액이 부족합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # F expression으로 잔액에서 차감
        wallet.coin = F("coin") - coin_amount
        wallet.save()
        wallet.refresh_from_db()

        return Response({"message": "코인이 성공적으로 차감되었습니다.", "coin": wallet.coin}, status=status.HTTP_200_OK)


class WalletAdminRechargeView(APIView):
    serializer_class = WalletRechargeSerializer

    def post(self, request, user_id):
        user = User.objects.get_user_by_id(user_id=user_id)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        coin_amount = serializer.validated_data["coin"]

        wallet = Wallet.objects.filter(user_id=user.id).first()
        if not wallet:
            return Response({"error": "지갑을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # F expression을 사용하여 동시성 문제 해결
        wallet.coin = F("coin") + coin_amount
        wallet.save()

        # 다시 데이터베이스에서 값 가져오기
        wallet.refresh_from_db()

        return Response({"message": "코인이 성공적으로 충전되었습니다.", "coin": wallet.coin}, status=status.HTTP_200_OK)
