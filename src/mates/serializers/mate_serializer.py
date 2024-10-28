from django.db.models.aggregates import Avg
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
        # 특정 game_id에 대한 리뷰 개수를 반환
        return Review.objects.filter(game_request__game_id=obj.game_id).count()

    def get_average_rating(self, obj):
        # 특정 game_id에 대한 평균 평점을 반환
        average = Review.objects.filter(game_request__game_id=obj.game_id).aggregate(Avg("rating"))["rating__avg"]
        return round(average, 2) if average is not None else 0  # 리뷰가 없는 경우 0 반환
