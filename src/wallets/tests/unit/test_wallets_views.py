from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from wallets.models.wallets_model import Wallet


class WalletBalanceViewTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # 유저 생성 (지갑은 자동으로 생성됨)
        cls.user = User.objects.create_user(email="testuser@example.com", password="password123", social_provider="google")

        # 유저의 토큰 생성
        refresh = RefreshToken.for_user(cls.user)
        cls.access_token = str(refresh.access_token)

        # 지갑의 초기 잔액을 설정
        cls.wallet = Wallet.objects.get(user=cls.user)
        cls.wallet.coin = 100
        cls.wallet.save()

    def setUp(self):
        # 각 테스트마다 인증 헤더 설정
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_wallet_balance_success(self):
        # When: 지갑 잔액을 조회하는 요청을 보낸다.
        url = reverse("user-coin-wallet")
        response = self.client.get(url)

        # Then: 잔액이 정상적으로 반환되는지 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user_id"], self.user.id)
        self.assertEqual(response.data["coin"], 100)

    def test_wallet_recharge(self):
        # Given: 지갑에 50 코인을 충전
        url = reverse("user-coin-recharge")
        data = {"coin": 50}
        response = self.client.post(url, data, format="json")

        # Then: 충전이 성공적으로 완료되는지 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 잔액이 150으로 증가했는지 확인
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.coin, 150)


class WalletWithdrawViewTest(APITestCase):
    def setUp(self):
        # 테스트용 유저 생성
        self.user = User.objects.create_user(email="testuser@example.com", password="password123", social_provider="google")

        # 지갑 생성 및 초기 코인 설정
        self.wallet, created = Wallet.objects.get_or_create(user=self.user)
        self.wallet.coin = 100  # 초기 코인 설정을 강제
        self.wallet.save()
        self.wallet.refresh_from_db()  # 최신 데이터 반영

        # JWT 토큰 생성
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # 인증 헤더 설정
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        # 차감 API URL 설정
        self.url = reverse("user-coin-withdraw")

    def test_withdraw_success(self):
        # Given: 충분한 코인 양으로 차감 요청
        data = {"coin": 50}

        # When: POST 요청을 통해 코인 차감
        response = self.client.post(self.url, data, format="json")

        # Then: 응답 상태 코드가 200이고, 코인이 차감된 후 잔액 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "코인이 성공적으로 차감되었습니다.")
        self.assertEqual(response.data["coin"], 50)

    def test_withdraw_insufficient_balance(self):
        # Given: 잔액보다 많은 코인 차감 요청
        data = {"coin": 150}  # 현재 잔액은 100

        # When: POST 요청을 통해 코인 차감 시도
        response = self.client.post(self.url, data, format="json")

        # Then: 잔액 부족으로 400 Bad Request 응답
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("coin", response.data)
        self.assertEqual(response.data["coin"][0], "잔액이 부족합니다.")

    def test_withdraw_invalid_coin_amount(self):
        # Given: 0 이하의 코인 차감 요청
        data = {"coin": -10}  # 유효하지 않은 코인 양

        # When: POST 요청을 통해 코인 차감 시도
        response = self.client.post(self.url, data, format="json")

        # Then: 유효하지 않은 코인 양으로 400 Bad Request 응답
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("coin", response.data)
        self.assertEqual(response.data["coin"][0], "차감할 코인 양은 1 이상이어야 합니다.")
