from django.test import TestCase

from chats.models import ChatRoom, ChatRoomUser, Message
from users.models import User


class ChatRoomModelTest(TestCase):
    def setUp(self):
        self.main_user = User.objects.create_user(nickname="하하", social_provider="google", email="haha@haha.com")
        self.other_user = User.objects.create_user(nickname="이이", social_provider="google", email="ee@ee.com")
        self.chatroom = ChatRoom.objects.create()
        self.chatroom_user1 = ChatRoomUser.objects.create(chatroom=self.chatroom, user=self.main_user)
        self.chatroom_user2 = ChatRoomUser.objects.create(chatroom=self.chatroom, user=self.other_user)

    def test_chat_room_creation(self):
        self.assertEqual(self.chatroom_user1.user, self.main_user)
        self.assertEqual(self.chatroom_user2.user, self.other_user)


class MessageModelTest(TestCase):
    def setUp(self):
        self.main_user = User.objects.create_user(nickname="하하", social_provider="google", email="haha@haha.com")
        self.other_user = User.objects.create_user(nickname="이이", social_provider="google", email="ee@ee.com")
        self.chatroom = ChatRoom.objects.create()
        ChatRoomUser.objects.create(chatroom=self.chatroom, user=self.main_user)
        ChatRoomUser.objects.create(chatroom=self.chatroom, user=self.other_user)

        self.message = Message.objects.create(room=self.chatroom, sender=self.main_user, text="하이")

    def test_message_creation(self):
        self.assertEqual(self.message.sender, self.main_user)
        self.assertEqual(self.message.text, "하이")
        self.assertEqual(self.message.room, self.chatroom)
