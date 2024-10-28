from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from reviews.models import Review
from reviews.serializers.serializers import AllReviewSerializer, ReviewSerializer
from reviews.utils import ReviewPagination


class ReviewListView(ListCreateAPIView):
    serializer_class = AllReviewSerializer
    pagination_class = ReviewPagination

    def get_queryset(self):
        return Review.objects.all().order_by("-created_at")

    def list(self, request, *args, **kwargs):
        try:
            # 기본 ListAPIView의 list 메서드를 호출하여 리뷰 목록을 반환
            return super().list(request, *args, **kwargs)
        except Exception as e:
            # 예외가 발생하면 400 에러와 함께 오류 메시지를 반환
            return Response({"error": "리뷰 조회에 실패하였습니다."}, status=status.HTTP_400_BAD_REQUEST)


class GameReviewCreateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        data = request.data.copy()
        data["user"] = request.user.id

        # 게임 요청 ID를 가져옵니다.
        game_request_id = data.get("game_request")

        # 해당 게임 요청에 대한 리뷰가 이미 존재하는지 확인
        if Review.objects.filter(game_request_id=game_request_id).exists():
            return Response({"error": "해당 게임 요청에 대한 리뷰는 이미 존재합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 요청 의뢰로부터 리뷰를 생성할 수 있도록 시리얼라이저 사용
        serializer = AllReviewSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()  # 유저 정보 추가
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


# 1. 특정 게임 의뢰에 대한 리뷰 조회
class GameRequestReviewListAPIView(APIView):
    pagination_class = ReviewPagination

    def get(self, request, game_request_id):
        reviews = Review.objects.filter(game_request_id=game_request_id).order_by("-created_at")

        paginator = self.pagination_class()
        paginated_reviews = paginator.paginate_queryset(reviews, request)

        # 기존 PaginatedReviewSerializer 대신 pagination_class를 통해 응답 생성
        serializer = ReviewSerializer(paginated_reviews, many=True)
        return paginator.get_paginated_response(serializer.data)


# 2. 특정 사용자의 특정 게임 리뷰 조회
class UserGameReviewListAPIView(APIView):
    pagination_class = ReviewPagination

    def get(self, request, user_id, game_id):
        reviews = Review.objects.filter(game_request__user_id=user_id, game_request__game_id=game_id).order_by("-created_at")

        paginator = self.pagination_class()
        paginated_reviews = paginator.paginate_queryset(reviews, request)

        serializer = ReviewSerializer(paginated_reviews, many=True)
        return paginator.get_paginated_response(serializer.data)


# 3. 특정 사용자의 전체 리뷰 조회
class UserReviewListAPIView(APIView):
    pagination_class = ReviewPagination

    def get(self, request, user_id):

        reviews = Review.objects.filter(game_request__user_id=user_id).order_by("-created_at")

        paginator = self.pagination_class()
        paginated_reviews = paginator.paginate_queryset(reviews, request)
        serializer = ReviewSerializer(paginated_reviews, many=True)
        response = paginator.get_paginated_response(serializer.data)

        return response
