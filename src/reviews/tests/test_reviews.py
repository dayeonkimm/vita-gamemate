from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from game_requests.models import GameRequest
from games.models import Game
from reviews.models import Review
from users.models.user_model import User


class ReviewListViewTest(TestCase):
    # 리뷰 리스트 조회

    def setUp(self):
        # Given: 리뷰 데이터가 데이터베이스에 존재할 때

        self.user1 = User.objects.create(nickname="user1", email="user1@example.com")
        self.user2 = User.objects.create(nickname="user2", email="user2@example.com")
        self.game = Game.objects.create(name="리그오브레전드")
        # GameRequest 생성 시 user_id와 mate_id 제공
        self.game_request = GameRequest.objects.create(
            user_id=self.user1.id, mate_id=self.user2.id, game=self.game, price=3000  # user_id에 user1 할당  # mate_id에 user2 할당
        )

        # 한 게밍 당 한 리뷰만 생성할 수 있기 때문에 개별적으로 생성
        # 첫 번째 GameRequest 생성
        self.game_request_1 = GameRequest.objects.create(user_id=self.user1.id, mate_id=self.user2.id, game=self.game, price=3000)
        self.game_request_1.title = "게임 요청 1"
        Review.objects.create(game_request=self.game_request_1, rating=5.0, content="와 진짜 재밌다")

        # 두 번째 GameRequest 생성
        self.game_request_2 = GameRequest.objects.create(user_id=self.user1.id, mate_id=self.user2.id, game=self.game, price=4000)
        self.game_request_2.title = "게임 요청 2"
        Review.objects.create(game_request=self.game_request_2, rating=1.0, content="와 진짜 노잼")

    def test_review_list_view(self):
        # When: 리뷰 목록을 요청했을 때
        url = reverse("reviews")

        response = self.client.get(url)

        # Then: 최신 순으로 리뷰가 반환되고, 한 페이지에 최대 10개의 리뷰가 있어야 한다
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)  # 데이터베이스에 2개의 리뷰가 있으므로
        self.assertEqual(response.data["results"][0]["content"], "와 진짜 노잼")  # 최신 리뷰가 첫 번째로 와야 함
        self.assertEqual(response.data["results"][1]["content"], "와 진짜 재밌다")

    def test_review_list_view_with_exception(self):
        # When: 예외가 발생했을 때
        url = reverse("reviews")  # 리뷰 목록 조회 url

        # Mock를 통해 list 메서드가 예외를 던지도록 만듬
        with patch("reviews.models.Review.objects.all", side_effect=Exception("DB Error")):
            response = self.client.get(url)
        # patch 사용하여 review 모델의 objects.all() 메서드 임시로 바꿈
        # DB Error 예외 발생 - 리뷰 목록 조회시 DB에 문제 발생 시뮬레이션

        # Then: 400 에러와 함께 오류 메시지가 반환되어야 한다
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "리뷰 조회에 실패하였습니다.")


class GameReviewCreateAPIViewTest(APITestCase):

    def setUp(self):
        # Given: 필요한 데이터 준비
        self.user1 = User.objects.create(nickname="user1", email="user1@example.com")
        self.user2 = User.objects.create(nickname="user2", email="user2@example.com")
        self.game = Game.objects.create(name="리그오브레전드")

        # GameRequest 생성
        self.game_request = GameRequest.objects.create(
            user_id=self.user1.id,
            mate_id=self.user2.id,
            game=self.game,
            price=3000,
        )
        self.game_request.title = "게임 목록 조회"

        self.refresh = RefreshToken.for_user(self.user1)

        # URL 정의
        self.url = reverse("review-write", kwargs={"game_request_id": self.game_request.id})

    def test_create_review_success(self):  # 성공
        # When: 올바른 데이터로 리뷰를 생성 요청

        new_game_request = GameRequest.objects.create(
            user_id=self.user1.id,
            mate_id=self.user2.id,
            game=self.game,
            price=3000,
        )

        # When: 올바른 데이터로 리뷰를 생성 요청
        data = {"game_request": new_game_request.id, "rating": 5.0, "content": "아 짱 좋아요"}

        response = self.client.post(self.url, data, format="json", HTTP_AUTHORIZATION=f"Bearer {str(self.refresh.access_token)}")

        # Then: 성공적으로 리뷰가 생성되고 201 응답을 받아야 함
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)  # 리뷰가 하나 생성되어야 함
        self.assertEqual(response.data["content"], "아 짱 좋아요")  # 내용 확인

    def test_create_review_already_exists(self):
        # Given: 동일한 게임 요청에 대한 리뷰가 이미 존재할 때
        # 이미 존재하는 리뷰를 DB에 생성 / 중복 리뷰 방지
        Review.objects.create(game_request=self.game_request, rating=5.0, content="이미 존재하는 리뷰")

        # When: 동일한 게임 요청으로 리뷰 생성 시도
        # 이미 리뷰 존재하는 game_request에 새로운 래뷰 생성 시도
        data = {"game_request": self.game_request.id, "rating": 4.0, "content": "새로운 리뷰"}
        response = self.client.post(self.url, data, format="json", HTTP_AUTHORIZATION=f"Bearer {str(self.refresh.access_token)}")
        # 올바른 인증 토큰 사용 - self.client.post()에 post 요청

        # Then: 400 Bad Request 응답을 받아야 하고, 오류 메시지가 포함
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "해당 게임 요청에 대한 리뷰는 이미 존재합니다.")

    def test_create_review_missing_authorization(self):  # 성공
        # When: 인증 없이 리뷰 생성 요청

        data = {"game_request": self.game_request.id, "rating": 5.0, "content": "아 짱 좋아요"}
        response = self.client.post(self.url, data, format="json")
        # Then: 401 Unauthorized 응답을 받아야 함
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_create_review_game_request_not_found(self):  # 성공
        # When: 존재하지 않는 게임 요청으로 리뷰 생성 요청
        self.client.force_authenticate(user=self.user1)

        # 존재하지 않는 game_request_id 사용
        url = reverse("review-write", kwargs={"game_request_id": 99999})  # 유효하지 않은 game_request_id
        data = {"rating": 5.0, "content": "아 짱 좋아요"}

        response = self.client.post(url, data, format="json")

        # Then: 400 Bad Request 응답을 받아야 함
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "유효하지 않은 게임 요청입니다.")

    def test_create_review_invalid_rating(self):
        # When: 잘못된 평점으로 리뷰 생성 요청
        self.client.force_authenticate(user=self.user1)

        data = {"game_request": self.game_request.id, "rating": 6.0, "content": "아 짱 좋아요"}  # 유효하지 않은 평점
        response = self.client.post(self.url, data, format="json")

        # Then: 400 Bad Request 응답을 받아야 하고 오류 메시지가 포함되어야 함
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data["rating"][0]), "평점은 1.0에서 5.0 사이여야 합니다.")
