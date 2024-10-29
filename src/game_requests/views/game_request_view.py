from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from game_requests.models import GameRequest
from game_requests.serializers.game_request_serializer import (
    GameRequestAcceptSerializer,
    GameRequestCreateSerializer,
    GameRequestOrderedSerializer,
    GameRequestReceivedSerializer,
)
from game_requests.utils import GameRequestPagination
from mates.models import MateGameInfo
from users.exceptions import UserNotFound
from users.models import User


class GameRequestCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        try:
            mate = User.objects.get_mate_user(user_id=user_id, is_mate=True)

        except UserNotFound:
            return Response({"error": "사용자를 찾지 못했습니다."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        if user_id == user.id:
            return Response({"error": "자신에게 의뢰 할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        game_id = request.data.get("game_id")

        if not MateGameInfo.objects.get_mate_game_info_from_id_and_game_id(mate_id=mate.id, game_id=game_id):
            return Response({"error": "해당 메이트에게 등록된 해당 게임이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = GameRequestCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        GameRequest.objects.create(user_id=user.id, mate_id=mate.id, **serializer.validated_data)

        return Response({"message": "의뢰가 접수 되었습니다."}, status=status.HTTP_201_CREATED)


class GameRequestOrderedAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = GameRequestPagination

    def get(self, request):
        user = request.user

        game_requests = GameRequest.objects.filter(user=user).order_by("-created_at")

        paginator = self.pagination_class()
        paginated_requests = paginator.paginate_queryset(game_requests, request)

        serializer = GameRequestOrderedSerializer(paginated_requests, many=True)

        return paginator.get_paginated_response(serializer.data)


class GameRequestReceivedAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = GameRequestPagination

    def get(self, request):
        mate = request.user

        game_requests = GameRequest.objects.filter(mate=mate).order_by("-created_at")

        paginator = self.pagination_class()
        paginated_requests = paginator.paginate_queryset(game_requests, request)

        serializer = GameRequestReceivedSerializer(paginated_requests, many=True)

        return paginator.get_paginated_response(serializer.data)


class GameRequestAcceptAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, game_request_id):
        mate = request.user

        try:
            game_request = GameRequest.objects.get_game_request_from_id(id=game_request_id)

        except GameRequest.DoesNotExist:
            return Response({"error": "해당하는 게임 의뢰를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        if not game_request.mate.id == mate.id:
            return Response({"error": "메이트 사용자가 일치 하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        if game_request.status is True:
            return Response({"error": "이미 해당하는 게임 의뢰를 수락했습니다."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = GameRequestAcceptSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        is_accept = serializer.validated_data.get("is_accept")

        if is_accept is False:
            GameRequest.objects.reject(game_request)
            return Response({"message": "의뢰를 거절하였습니다."}, status=status.HTTP_200_OK)

        if is_accept is True:
            GameRequest.objects.accept(game_request)
            return Response({"message": "의뢰를 수락했습니다."}, status=status.HTTP_200_OK)
