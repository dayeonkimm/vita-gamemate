from django.test import TestCase

from game_requests.models import GameRequest
from games.models import Game
from users.models.user_model import User


class GameRequestModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            nickname="user1",
            email="user1@example.com",
            gender="male",
            social_provider="google",
        )
        self.mate = User.objects.create_user(
            nickname="user2",
            email="user2@example.com",
            gender="female",
            social_provider="google",
        )
        self.game = Game.objects.get(
            name="lol",
        )
        self.game_request = GameRequest.objects.create(
            game=self.game,
            user_id=self.user.id,
            mate_id=self.mate.id,
            price=1000,
            amount=2,
        )

    def test_create_game_request(self):

        self.assertEqual(self.game_request.game, self.game)
        self.assertEqual(self.game_request.user, self.user)
        self.assertEqual(self.game_request.mate, self.mate)
        self.assertEqual(self.game_request.price, 1000)
        self.assertEqual(self.game_request.amount, 2)
        self.assertFalse(self.game_request.status)

    def test_accept_game_request(self):
        game_request = GameRequest.objects.accept(self.game_request)
        self.assertTrue(game_request.status)

    def test_reject_game_request(self):
        GameRequest.objects.reject(self.game_request)
        self.assertFalse(GameRequest.objects.filter(id=self.game_request.id).exists())
