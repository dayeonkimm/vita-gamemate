from multiprocessing import Value

from django.core.exceptions import ValidationError
from django.db.models import (
    Avg,
    BooleanField,
    Case,
    FloatField,
    IntegerField,
    OuterRef,
    Subquery,
    When,
)
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from game_requests.models import GameRequest
from mates.exceptions import InvalidLevelError
from mates.models import MateGameInfo
from mates.serializers.mate_serializer import RegisterMateSerializer
from mates.utils import MateGameInfoPagination
from users.models import User
from users.serializers.user_serializer import UserMateSerializer


class RegisterMateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        serializer = RegisterMateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            # serializer.errors 로 정확한 에러 출력

        try:
            MateGameInfo.objects.create(user_id=user.id, **serializer.validated_data)

        except ValidationError:
            return Response({"error": "이미 해당 게임이 등록 되어 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

        except InvalidLevelError as e:
            return Response({"error": str(e)}, status=e.status_code)

        return Response({"message": "메이트 등록이 완료되었습니다."}, status=status.HTTP_201_CREATED)


class MateGameInfoListView(generics.ListAPIView):
    serializer_class = UserMateSerializer
    pagination_class = MateGameInfoPagination  # 페이지네이션 설정

    def get_queryset(self):
        game_id = self.kwargs.get("game_id")

        if game_id:
            queryset = User.objects.filter(mategameinfo__game_id=game_id)
        else:
            queryset = User.objects.filter(mategameinfo__isnull=False)

        gender = self.request.query_params.get("gender", "all")

        if gender in ["male", "female"]:
            queryset = queryset.filter(gender=gender)

        level = self.request.query_params.get("level")

        if level:
            level_list = level.split(",")
            queryset = queryset.filter(mategameinfo__level__in=level_list)

        sort = self.request.query_params.get("sort")

        if sort == "recommendation":
            # profile_image가 없는 유저 안 나타나게
            queryset = queryset.exclude(profile_image="").filter(profile_image__isnull=False).order_by("-mategameinfo__created_at")

        elif sort == "new":
            queryset = queryset.order_by("-mategameinfo__created_at")

        elif sort == "rating_desc":
            # 서브쿼리를 통해 평균 평점 계산
            avg_rating_subquery = (
                GameRequest.objects.filter(mate=OuterRef("pk"), review__isnull=False)
                .values("mate")
                .annotate(avg_rating=Avg("review__rating"))
                .values("avg_rating")
            )

            # 평균 평점에 따른 정렬 처리
            queryset = (
                queryset.annotate(
                    avg_rating=Subquery(avg_rating_subquery[:1]),
                )
                .annotate(
                    avg_rating=Case(
                        When(avg_rating__isnull=True, then=0),  # 평균 평점이 없으면 0으로 설정
                        default="avg_rating",
                        output_field=FloatField(),
                    )
                )
                .order_by("-avg_rating")
            )

        elif sort == "price_asc":
            queryset = queryset.order_by("mategameinfo__request_price")

        elif sort == "price_desc":
            queryset = queryset.order_by("-mategameinfo__request_price")

        return queryset.distinct()
