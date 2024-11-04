import json
from unittest import mock
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from payments.models import Payment

User = get_user_model()


class TossPaymentViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(nickname="testuser", email="testuser@gmail.com", social_provider="kakao")
        self.client.force_authenticate(user=self.user)

        self.url = reverse("toss-payment")
        self.valid_data = {
            "payment_key": "valid_payment_key",
            "order_id": "test_order_id",
            "amount": 1000,
        }

    @patch("requests.post")
    def test_successful_payment(self, mock_post):
        # 모의 응답 설정
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "orderName": "Test Order",
            "method": "카드",
            "status": "DONE",
            "requestedAt": "2024-11-03T12:00:00Z",
            "approvedAt": "2024-11-03T12:01:00Z",
        }

        response = self.client.post(self.url, data=self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "결제 성공")
        self.assertEqual(response.data["payment"]["order_name"], "Test Order")
        self.assertEqual(response.data["payment"]["status"], "DONE")

    @patch("requests.post")
    def test_failed_payment(self, mock_post):
        # 결제 실패 모의 응답 설정
        mock_post.return_value.status_code = 400

        response = self.client.post(self.url, data=self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "결제를 실패했습니다")

    def test_invalid_payment_data(self):
        invalid_data = {
            "payment_key": "valid_payment_key",
            "order_id": "test_order_id",
        }
        response = self.client.post(self.url, data=invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amount", response.data)


class UserPaymentListViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(nickname="testuser", email="testuser@gmail.com", social_provider="kakao")
        self.client.force_authenticate(user=self.user)

        self.url = reverse("my-payments")

        self.payment = Payment.objects.create(
            user=self.user,
            payment_key="sample_key",
            order_id="sample_order_id",
            order_name="Sample Order",
            method="카드",
            status="DONE",
            amount=1000,
            requested_at="2024-11-03T12:00:00Z",
            approved_at="2024-11-03T12:01:00Z",
        )

    def test_list_payments(self):
        response = self.client.get(self.url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["order_id"], "sample_order_id")
        self.assertEqual(response.data[0]["amount"], 1000)
        self.assertEqual(response.data[0]["status"], "DONE")
