from django.db.models.aggregates import Avg, Count
from rest_framework import serializers

from games.models import Game
from mates.models import MateGameInfo
from reviews.models import Review


class RegisterMateSerializer(serializers.ModelSerializer):
    game_id = serializers.PrimaryKeyRelatedField(
        source="game",
        queryset=Game.objects.all(),
        write_only=True,
    )

    class Meta:
        model = MateGameInfo
        exclude = [
            "id",
            "user",
            "game",
            "updated_at",
            "created_at",
        ]


class MateGameInfoSerializer(serializers.ModelSerializer):
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = MateGameInfo
        fields = [
            "game_id",
            "description",
            "image",
            "level",
            "request_price",
            "review_count",
            "average_rating",
        ]

    def get_review_count(self, obj):
        # 캐시를 활용해 동일한 쿼리를 재사용
        if not hasattr(obj, "_review_data"):
            obj._review_data = Review.objects.filter(game_request__game_id=obj.game_id).aggregate(
                review_count=Count("id"), average_rating=Avg("rating")
            )
        return obj._review_data["review_count"] or 0

    def get_average_rating(self, obj):
        # 이미 캐싱된 _review_data 에서 평균 평점 값을 가져옴
        if hasattr(obj, "_review_data"):
            average = obj._review_data["average_rating"]
            return round(average, 2) if average is not None else 0
        return 0
