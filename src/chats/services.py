import logging
from urllib.parse import urlparse

import redis
from django.conf import settings
from django.db.models import F

from .models import ChatRoom, ChatRoomUser, Message

logger = logging.getLogger(__name__)


def get_redis_client():
    try:
        redis_url = settings.CHANNEL_LAYERS["default"]["CONFIG"]["hosts"][0]
        parsed_url = urlparse(redis_url)

        client = redis.Redis(
            host=parsed_url.hostname,
            port=parsed_url.port,
            password=parsed_url.password,
            db=2,  # 채널 레이어와 다른 데이터베이스 사용 (예: 2번)
        )
        client.ping()  # 연결 테스트
        return client
    except Exception as e:
        logger.error(f"Redis 연결 실패: {str(e)}")
        return None


redis_client = get_redis_client()


class ChatService:
    @staticmethod
    def get_unread_count(room_id, user_id):
        cache_key = f"unread_count:{room_id}:{user_id}"

        cached_count = redis_client.get(cache_key)
        if cached_count is not None:
            return int(cached_count)

        chatroom_user = ChatRoomUser.objects.get(chatroom_id=room_id, user_id=user_id)
        count = chatroom_user.unread_count

        redis_client.setex(cache_key, 300, count)

        return count

    @staticmethod
    def increment_unread_count(room_id, receiver_id):
        # 데이터베이스 업데이트
        ChatRoomUser.objects.filter(chatroom_id=room_id, user_id=receiver_id).update(unread_count=F("unread_count") + 1)
        # Redis 캐시 업데이트
        if redis_client is not None:
            cache_key = f"unread_count:{room_id}:{receiver_id}"
            redis_client.incr(cache_key)

    @staticmethod
    def reset_unread_count(room_id, user_id):
        chatroom_user = ChatRoomUser.objects.get(chatroom_id=room_id, user_id=user_id)
        chatroom_user.unread_count = 0
        chatroom_user.save()

        cache_key = f"unread_count:{room_id}:{user_id}"
        redis_client.set(cache_key, 0)

    # @staticmethod
    # def get_user_chatrooms(user_id):
    #     chatrooms = ChatRoom.objects.filter(chatroomuser__user_id=user_id)
    #     result = []
    #     for chatroom in chatrooms:
    #         unread_count = ChatService.get_unread_count(chatroom.id, user_id)
    #         result.append({
    #             'id': chatroom.id,
    #             'name': chatroom.name,
    #             'unread_count': unread_count,
    #             'latest_message': chatroom.message_set.order_by('-created_at').first()
    #         })
    #     return result
