from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from game_requests.models import GameRequest
from games.models import Game
from users.models import User


class ReviewSerializerValidationTestCase(APITestCase):

    def setUp(self):
        # 유저와 메이트 생성
        self.user = User.objects.create_user(
            nickname="사용자임",
            email="user1@example.com",
            gender="male",
            social_provider="google",
        )
        self.other_user = User.objects.create_user(
            nickname="다른사용자",
            email="user2@example.com",
            gender="female",
            social_provider="google",
        )

        # 게임과 게임 요청 생성
        self.game = Game.objects.create(name="lol")
        self.game_request = GameRequest.objects.create(
            user_id=self.user.id, mate_id=self.other_user.id, game=self.game, price=500, amount=1  # user ID로 설정  # mate ID로 설정
        )

    def test_validate_review_with_correct_user(self):
        # 올바른 사용자가 자신의 게임 요청에 리뷰를 작성할 수 있는지 확인
        self.client.force_authenticate(user=self.user)

        url = reverse("review-write")
        data = {
            "game_request": self.game_request.id,
            "rating": 4.0,
            "content": "정상적인 리뷰 작성",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], "정상적인 리뷰 작성")
        self.assertEqual(response.data["rating"], 4.0)

    def test_validate_review_with_incorrect_user(self):
        # 다른 사용자가 리뷰를 작성하려 할 때 유효성 검사에서 실패하는지 확인
        self.client.force_authenticate(user=self.other_user)  # 다른 사용자로 인증 변경

        url = reverse("review-write")
        data = {
            "game_request": self.game_request.id,
            "rating": 4.0,
            "content": "다른 사용자가 작성하는 리뷰",
        }
        response = self.client.post(url, data)

        # 유효성 검사 실패 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(response.data["non_field_errors"][0], "본인이 의뢰한 게임에 대해서만 리뷰를 작성할 수 있습니다.")
