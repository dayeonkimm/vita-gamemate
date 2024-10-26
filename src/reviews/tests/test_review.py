from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from game_requests.models import GameRequest
from games.models import Game
from mates.models import MateGameInfo
from reviews.models import Review
from users.models import User


class ReviewAPITestCase(TestCase):

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
        self.game_request = GameRequest.objects.create(user_id=self.user.id, mate_id=self.mate.id, game=self.game, price=500, amount=1)

        # 리뷰 생성
        Review.objects.create(game_request=self.game_request, rating=5, content="리뷰 내용 1")

    def test_game_request_review_list(self):
        # 특정 게임 의뢰의 리뷰 목록 조회 테스트
        url = reverse("reviews-request", kwargs={"game_request_id": self.game_request.id})
        response = self.client.get(url, data={"page": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 응답 데이터 출력 (디버깅용)
        print(response.data)

        # 응답 데이터 확인 (리뷰가 1개 있는지 확인)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["content"], "리뷰 내용 1")

        # 추가된 필드 확인 (author_id, author_nickname, maet_nickname)
        self.assertEqual(response.data["results"][0]["author_id"], self.user.id)
        self.assertEqual(response.data["results"][0]["author_nickname"], "사용자임")
        self.assertEqual(response.data["results"][0]["maet_nickname"], "mate임")

    def test_user_game_review_list(self):
        # 특정 사용자의 특정 게임에 대한 리뷰 목록 조회 테스트
        url = reverse("review-game", kwargs={"user_id": self.user.id, "game_id": self.game.id})

        # 쿼리 파라미터로 페이지 번호 전달
        response = self.client.get(f"{url}?page=1")

        # 200 응답 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 응답 데이터 확인 (리뷰는 1개만 있어야 함)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)

        # 추가된 필드 확인 (author_id, author_nickname, maet_nickname)
        self.assertEqual(response.data["results"][0]["author_id"], self.user.id)
        self.assertEqual(response.data["results"][0]["author_nickname"], "사용자임")
        self.assertEqual(response.data["results"][0]["maet_nickname"], "mate임")

        # 페이지네이션 확인 (리뷰가 1개이므로 페이지네이션이 없을 것)
        self.assertIsNone(response.data.get("next"))  # 다음 페이지 링크가 없어야 함
        self.assertIsNone(response.data.get("previous"))  # 이전 페이지 링크가 없어야 함
