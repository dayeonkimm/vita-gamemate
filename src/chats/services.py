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
        try:
            cache_key = f"unread_count:{room_id}:{user_id}"

            if redis_client is not None:
                cached_count = redis_client.get(cache_key)
                if cached_count is not None:
                    return int(cached_count)

            chatroom_user = ChatRoomUser.objects.get(chatroom_id=room_id, user_id=user_id)
            count = chatroom_user.unread_count

            if redis_client is not None:
                redis_client.setex(cache_key, 300, count)

            return count
        except redis.RedisError as e:
            logger.error(f"Redis error in get_unread_count: {str(e)}")
        except ChatRoomUser.DoesNotExist:
            logger.error(f"ChatRoomUser not found for room_id={room_id}, user_id={user_id}")
            return 0
        except Exception as e:
            logger.error(f"Unexpected error in get_unread_count: {str(e)}")
            return 0

    @staticmethod
    def increment_unread_count(room_id, receiver_id):
        try:
            updated = ChatRoomUser.objects.filter(chatroom_id=room_id, user_id=receiver_id).update(unread_count=F("unread_count") + 1)

            if updated == 0:
                logger.warning(f"No ChatRoomUser found for room_id={room_id}, receiver_id={receiver_id}")
                return

            if redis_client is not None:
                try:
                    cache_key = f"unread_count:{room_id}:{receiver_id}"
                    redis_client.incr(cache_key)
                except redis.RedisError as e:
                    logger.error(f"Redis error in increment_unread_count: {str(e)}")
            else:
                logger.warning("Redis client is not available. Skipping cache update.")

        except Exception as e:
            logger.error(f"Unexpected error in increment_unread_count: {str(e)}")

    @staticmethod
    def reset_unread_count(room_id, user_id):
        try:
            # 데이터베이스 업데이트
            chatroom_user = ChatRoomUser.objects.get(chatroom_id=room_id, user_id=user_id)
            chatroom_user.unread_count = 0
            chatroom_user.save()

            # Redis 캐시 업데이트
            if redis_client is not None:
                cache_key = f"unread_count:{room_id}:{user_id}"
                redis_client.set(cache_key, 0)
            else:
                logger.warning("Redis client is not available. Skipping cache update.")
        except redis.RedisError as e:
            logger.error(f"Redis error in reset_unread_count: {str(e)}")
        except ChatRoomUser.DoesNotExist:
            logger.error(f"ChatRoomUser not found for room_id={room_id}, user_id={user_id}")
        except Exception as e:
            logger.error(f"Unexpected error in reset_unread_count: {str(e)}")
