from django.conf import settings
from django.db.models import OuterRef, Subquery
from django.http import Http404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import User

from .models import ChatRoom, ChatRoomUser, Message
from .serializers import ChatRoomListSerializer, ChatRoomSerializer, MessageSerializer


class ChatRoomCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatRoomSerializer

    def create(self, request, *args, **kwargs):
        main_user = request.user
        other_user = self.get_other_user()

        existing_chatroom = self.get_existing_chatroom(main_user, other_user)
        if existing_chatroom:
            return self.handle_existing_chatroom(existing_chatroom, other_user)

        return self.create_new_chatroom(main_user, other_user)

    def get_other_user(self):
        other_user_nickname = self.request.data.get("other_user_nickname")
        if not other_user_nickname:
            raise ValidationError("other_user_nickname 파라미터가 필요합니다.")
        try:
            return User.objects.get(nickname=other_user_nickname)
        except User.DoesNotExist:
            raise ValidationError("해당 닉네임을 가진 사용자가 존재하지 않습니다.")

    def get_existing_chatroom(self, main_user, other_user):
        return ChatRoom.objects.filter(chatroom_users__user=main_user).filter(chatroom_users__user=other_user).first()

    def handle_existing_chatroom(self, chatroom, other_user):
        message = Message.objects.create(room=chatroom, sender=other_user, message=f"안녕하세요 {other_user.nickname}입니다")
        chatroom.update_latest_message(message)
        context = self.get_serializer_context()
        context.update(self.get_additional_context(chatroom, other_user))
        serializer = self.get_serializer(chatroom, context=context)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create_new_chatroom(self, main_user, other_user):
        chatroom = ChatRoom.objects.create()
        ChatRoomUser.objects.create(chatroom=chatroom, user=main_user)
        ChatRoomUser.objects.create(chatroom=chatroom, user=other_user)
        message = Message.objects.create(room=chatroom, sender=other_user, message=f"반갑습니다 {other_user.nickname}입니다")
        chatroom.update_latest_message(message)
        context = self.get_serializer_context()
        context.update(self.get_additional_context(chatroom, other_user))
        serializer = self.get_serializer(chatroom, context=context)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_additional_context(self, chatroom, other_user):
        return {
            "latest_message": chatroom.latest_message.message if chatroom.latest_message else None,
            "latest_message_time": chatroom.latest_message_time,
            "other_user_data": {
                "nickname": other_user.nickname,
                "id": other_user.id,
                "profile_image": other_user.profile_image.url if other_user.profile_image else None,
            },
        }


class ChatRoomListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatRoomListSerializer

    def get_queryset(self):
        user = self.request.user
        chatroom_users = ChatRoomUser.objects.filter(chatroom=OuterRef("pk")).values(
            "user__id", "user__nickname", "user__profile_image", "unread_count"
        )

        return (
            ChatRoom.objects.filter(chatroom_users__user=user)
            .select_related("latest_message__sender")
            .annotate(
                other_user_nickname=Subquery(chatroom_users.exclude(user__id=user.id).values("user__nickname")[:1]),
                other_user_id=Subquery(chatroom_users.exclude(user__id=user.id).values("user__id")[:1]),
                other_user_profile_image=Subquery(chatroom_users.exclude(user__id=user.id).values("user__profile_image")[:1]),
                unread_count=Subquery(chatroom_users.filter(user__id=user.id).values("unread_count")[:1]),
            )
            .order_by("-latest_message_time")
        )


class MessagePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class MessageListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    pagination_class = MessagePagination

    def get_queryset(self):
        user = self.request.user
        room_id = self.kwargs.get("room_id")

        if not room_id:
            raise ValidationError({"detail": "room_id 파라미터가 필요합니다."})

        queryset = Message.objects.filter(room_id=room_id).order_by("-created_at")

        if not queryset.exists():
            raise Http404("해당 room_id로 메시지를 찾을 수 없습니다.")

        return queryset
