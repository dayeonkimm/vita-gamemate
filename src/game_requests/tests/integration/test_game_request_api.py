from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from game_requests.models import GameRequest
from games.models import Game
from mates.models import MateGameInfo
from users.models import User


class GameRequestAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            nickname="사용자임",
            email="user1@example.com",
            gender="male",
            social_provider="google",
        )
        self.mate = User.objects.create_user(
            nickname="mate임",
            email="user2@example.com",
            gender="female",
            social_provider="google",
        )
        self.game = Game.objects.get(
            name="lol",
        )
        MateGameInfo.objects.create(
            user_id=self.mate.id,
            game=self.game,
            description="gg",
            level="챌린저",
            request_price=1000,
        )
        self.game_request = GameRequest.objects.create(
            game_id=self.game.id,
            user_id=self.user.id,
            mate_id=self.mate.id,
            price=100,
            amount=1,
        )

        self.url_create = reverse("game-request-create", kwargs={"user_id": self.mate.id})
        self.url_ordered = reverse("ordered-game-request")
        self.url_received = reverse("received-game-request")
        self.url_accept = reverse("accept-game-request", kwargs={"game_request_id": self.game_request.id})
        self.url_cancel = reverse("cancel-game-request", kwargs={"game_request_id": self.game_request.id})

        self.token = str(TokenObtainPairSerializer.get_token(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)

    def test_create_game_request_success(self):
        response = self.client.post(
            self.url_create,
            {
                "game_id": self.game.id,
                "price": 1000,
                "amount": 1,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_game_request_user_not_found(self):
        response = self.client.post(
            reverse("game-request-create", kwargs={"user_id": 456}),
            {
                "game_id": self.game.id,
                "price": 500,
                "amount": 1,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "사용자를 찾지 못했습니다."})

    def test_create_game_request_to_self(self):
        MateGameInfo.objects.create(
            user_id=self.user.id,
            game=self.game,
            description="gg",
            level="챌린저",
            request_price=1000,
        )
        response = self.client.post(
            reverse("game-request-create", kwargs={"user_id": self.user.id}),
            {
                "game_id": self.game.id,
                "price": 500,
                "amount": 1,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_game_request_no_game(self):
        response = self.client.post(
            reverse("game-request-create", kwargs={"user_id": self.mate.id}),
            {
                "game_id": 2,
                "price": 500,
                "amount": 1,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "해당 메이트에게 등록된 해당 게임이 없습니다."})

    def test_create_game_request_invalid_data(self):
        response = self.client.post(
            self.url_create,
            {
                "game_id": self.game.id,
                "price": -500,
                "amount": 1,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)

    def test_ordered_game_requests_success(self):
        GameRequest.objects.create(
            user_id=self.user.id,
            mate_id=self.mate.id,
            game_id=self.game.id,
            price=500,
            amount=1,
        )

        response = self.client.get(self.url_ordered)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["mate_nickname"], self.mate.nickname)

    def test_received_game_requests_success(self):
        self.token = str(TokenObtainPairSerializer.get_token(self.mate).access_token)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)

        GameRequest.objects.create(
            user_id=self.user.id,
            mate_id=self.mate.id,
            game_id=self.game.id,
            price=500,
            amount=1,
        )

        response = self.client.get(self.url_received)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["user_nickname"], self.user.nickname)

    def test_ordered_game_requests_no_requests(self):
        response = self.client.get(self.url_ordered)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_received_game_requests_no_requests(self):
        response = self.client.get(self.url_received)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_accept_game_requests_success(self):
        self.token = str(TokenObtainPairSerializer.get_token(self.mate).access_token)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)

        GameRequest.objects.create(
            user_id=self.user.id,
            mate_id=self.mate.id,
            game_id=self.game.id,
            price=500,
            amount=1,
        )

        response = self.client.post(self.url_accept, {"is_accept": True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "의뢰를 수락했습니다."})

    def test_reject_game_requests_success(self):
        self.token = str(TokenObtainPairSerializer.get_token(self.mate).access_token)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)

        self.game_request = GameRequest.objects.create(
            user_id=self.user.id,
            mate_id=self.mate.id,
            game_id=self.game.id,
            price=500,
            amount=1,
        )

        self.url_accept = reverse("accept-game-request", kwargs={"game_request_id": self.game_request.id})

        response = self.client.post(self.url_accept, {"is_accept": False})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "의뢰를 거절하였습니다."})
        self.assertEqual(GameRequest.objects.filter(id=self.game_request.id).exists(), False)

    def test_cancel_game_requests_success(self):
        response = self.client.post(self.url_cancel)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(GameRequest.objects.filter(id=self.game_request.id).exists())

    def test_accept_api_game_requests_not_found_game_request(self):
        self.token = str(TokenObtainPairSerializer.get_token(self.mate).access_token)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)

        self.url_accept = reverse("accept-game-request", kwargs={"game_request_id": 20})
        response = self.client.post(self.url_accept, {"is_accept": True})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "해당하는 게임 의뢰를 찾을 수 없습니다."})

    def test_accept_api_game_requests_already_accepted_game_request(self):
        self.token = str(TokenObtainPairSerializer.get_token(self.mate).access_token)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)

        GameRequest.objects.create(
            user_id=self.user.id,
            mate_id=self.mate.id,
            game_id=self.game.id,
            price=500,
            amount=1,
            status=True,
        )

        self.url_accept = reverse("accept-game-request", kwargs={"game_request_id": 2})
        response = self.client.post(self.url_accept, {"is_accept": True})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "이미 해당하는 게임 의뢰를 수락했습니다."})

    def test_accept_api_game_requests_not_match_mate_id(self):
        self.token = str(TokenObtainPairSerializer.get_token(self.mate).access_token)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)

        self.mate2 = User.objects.create_user(
            nickname="ma1te임",
            email="user2@example.2com",
            gender="female",
            social_provider="google",
        )

        game_request = GameRequest.objects.create(
            user_id=self.user.id,
            mate_id=self.mate2.id,
            game_id=self.game.id,
            price=500,
            amount=1,
            status=True,
        )

        self.url_accept = reverse("accept-game-request", kwargs={"game_request_id": game_request.id})
        response = self.client.post(self.url_accept, {"is_accept": True})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "메이트 사용자가 일치 하지 않습니다."})

    def test_accept_api_game_requests_not_valid_serializer(self):
        self.token = str(TokenObtainPairSerializer.get_token(self.mate).access_token)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)

        response = self.client.post(self.url_accept, {"is_accept": 123})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
