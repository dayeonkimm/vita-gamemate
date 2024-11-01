from django.db.models.aggregates import Avg, Count
from rest_framework import serializers

from game_requests.models import GameRequest
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
    game_request_count = serializers.SerializerMethodField()

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
            "game_request_count",
        ]

    def get_review_count(self, obj):
        mate_id = self.context.get("mate_id")

        if mate_id:
            return GameRequest.objects.get_game_request_game_review_count(mate_id=mate_id, game_id=obj.game_id)

        return 0

    def get_average_rating(self, obj):
        mate_id = self.context.get("mate_id")

        if mate_id:
            result = Review.objects.filter(  # review 모델의 커스텀 manager 가 없어서 이렇게 씀
                game_request__game_id=obj.game_id,
                game_request__mate_id=mate_id,
                game_request__review_status=True,
            ).aggregate(avg_rating=Avg("rating"))

            average = result["avg_rating"]
            return round(average, 2) if average is not None else 0

        return 0

    def get_game_request_count(self, obj):
        mate_id = self.context.get("mate_id")

        if mate_id:
            return GameRequest.objects.get_game_request_count(mate_id=mate_id, game_id=obj.game_id)

        return 0
