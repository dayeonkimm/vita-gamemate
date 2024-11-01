from django_redis import get_redis_connection
from rest_framework import serializers

from game_requests.models import GameRequest
from mates.serializers.mate_serializer import MateGameInfoSerializer
from users.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    is_online = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "nickname",
            "email",
            "gender",
            "profile_image",
            "birthday",
            "description",
            "social_provider",
            "is_mate",
            "is_online",
        ]
        extra_kwargs = {
            "email": {"required": False},
        }
        read_only_fields = [
            "id",
            "email",
            "social_provider",
            "is_mate",
        ]

    def get_is_online(self, user):
        redis_instance = get_redis_connection("default")

        is_online = redis_instance.get(f"user:{user.id}:is_online")

        if not is_online:
            return False

        return is_online.decode("utf-8").lower() == "true"


class UserMateSerializer(serializers.ModelSerializer):
    mate_game_info = serializers.SerializerMethodField()
    is_online = serializers.SerializerMethodField()
    total_request_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "nickname",
            "email",
            "gender",
            "profile_image",
            "birthday",
            "description",
            "social_provider",
            "is_mate",
            "is_online",
            "total_request_count",
            "mate_game_info",
        ]
        read_only_fields = [
            "id",
            "email",
            "social_provider",
            "is_mate",
        ]

    def get_mate_game_info(self, obj):
        mate_game_info = obj.mategameinfo_set.all()
        return MateGameInfoSerializer(mate_game_info, many=True, context={"mate_id": obj.id}).data

    def get_total_request_count(self, obj):
        return GameRequest.objects.get_game_request_total_count(mate_id=obj.id)

    def get_is_online(self, user):
        redis_instance = get_redis_connection("default")

        is_online = redis_instance.get(f"user:{user.id}:is_online")

        if not is_online:
            return False

        return is_online.decode("utf-8").lower() == "true"
