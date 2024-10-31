from django.conf import settings
from rest_framework import serializers

from .models import ChatRoom, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_nickname = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ("id", "sender_nickname", "message", "timestamp")

    def get_sender_nickname(self, obj):
        return obj.sender.nickname

    def get_timestamp(self, obj):
        return obj.created_at


class ChatRoomSerializer(serializers.ModelSerializer):
    latest_message = serializers.SerializerMethodField()
    main_user_nickname = serializers.SerializerMethodField()
    other_user_nickname = serializers.SerializerMethodField()
    other_user_id = serializers.SerializerMethodField()
    other_user_profile_image = serializers.SerializerMethodField()
    latest_message_time = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = (
            "id",
            "main_user_nickname",
            "other_user_nickname",
            "other_user_id",
            "other_user_profile_image",
            "latest_message",
            "latest_message_time",
            "updated_at",
        )

    def get_latest_message(self, obj):
        return self.context.get("latest_message")

    def get_latest_message_time(self, obj):
        return self.context.get("latest_message_time")

    def get_main_user_nickname(self, obj):
        return self.context["request"].user.nickname

    def get_other_user_nickname(self, obj):
        return self.context.get("other_user_data", {}).get("nickname")

    def get_other_user_id(self, obj):
        return self.context.get("other_user_data", {}).get("id")

    def get_other_user_profile_image(self, obj):
        return self.context.get("other_user_data", {}).get("profile_image")


class ChatRoomListSerializer(serializers.ModelSerializer):
    main_user_nickname = serializers.SerializerMethodField()
    other_user_nickname = serializers.CharField()
    other_user_id = serializers.IntegerField()
    other_user_profile_image = serializers.SerializerMethodField()
    latest_message = serializers.CharField(allow_null=True)
    latest_message_time = serializers.DateTimeField(allow_null=True)

    class Meta:
        model = ChatRoom
        fields = (
            "id",
            "main_user_nickname",
            "other_user_nickname",
            "other_user_id",
            "other_user_profile_image",
            "latest_message",
            "latest_message_time",
            "updated_at",
        )

    def get_main_user_nickname(self, obj):
        return self.context["request"].user.nickname

    def get_other_user_profile_image(self, obj):
        if obj.other_user_profile_image:
            return f"{settings.MEDIA_URL}{obj.other_user_profile_image}"
        return None
