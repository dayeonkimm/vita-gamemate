from django.urls import path

from chats import consumers

websocket_urlpatterns = [
    path("ws/chat/<int:room_id>/", consumers.ChatConsumer.as_asgi()),
    path("ws/chat/list/", consumers.ChatListConsumer.as_asgi()),
]
