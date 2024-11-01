from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class ChatRoom(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    latest_message = models.ForeignKey("Message", null=True, blank=True, on_delete=models.SET_NULL, related_name="latest_in_room")
    latest_message_time = models.DateTimeField(null=True, blank=True)

    def update_latest_message(self, message):
        self.latest_message = message
        self.latest_message_time = message.created_at
        self.save(update_fields=["latest_message", "latest_message_time"])


class ChatRoomUser(models.Model):
    chatroom = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="chatroom_users")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_chatrooms")
    unread_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ("chatroom", "user")


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="message_sender")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.room.update_latest_message(self)
