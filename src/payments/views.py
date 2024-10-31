import base64
import os

import requests
from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Payment
from .serializers import PaymentSerializer


class TossPaymentView(generics.GenericAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # 유효한 데이터 가져오기
            payment_key = serializer.validated_data["payment_key"]
            order_id = serializer.validated_data["order_id"]
            amount = serializer.validated_data["amount"]

            secret_key = os.environ.get("TOSS_TEST_SECRET_KEY")

            # Toss API 요청
            url = f"https://api.tosspayments.com/v1/payments/{payment_key}"
            headers = {
                "Authorization": "Basic " + base64.b64encode(f"{secret_key}:".encode()).decode(),
                "Content-Type": "application/json",
            }
            data = {
                "orderId": order_id,
                "amount": amount,
            }

            try:
                response = requests.post(url, json=data, headers=headers)
                response.raise_for_status()

                # Toss API에서 필요한 응답 데이터 가져오기
                response_data = response.json()
                order_name = response_data.get("orderName")
                method = response_data.get("method")
                payment_status = response_data.get("status")
                requested_at = response_data.get("requestedAt")
                approved_at = response_data.get("approvedAt")

                # 결제 정보 저장
                payment = Payment.objects.create(
                    user=user,
                    payment_key=payment_key,
                    order_id=order_id,
                    order_name=order_name,
                    method=method,
                    status=payment_status,
                    amount=amount,
                    requested_at=requested_at,
                    approved_at=approved_at,
                )

                payment_data = PaymentSerializer(payment).data

                return Response(
                    {
                        "title": "결제 성공",
                        "payment": payment_data,
                    },
                    status=status.HTTP_200_OK,
                )

            except requests.exceptions.RequestException as e:
                print(f"Toss 결제 API 오류: {e}")
                return Response({"detail": "결제 실패"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Payment.objects.filter(user=user).order_by("-requested_at")

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
