# chats/serializer의 경우 view와 엮여있어서 단독으로 unit test 불가
# main_user와 other_user를 구분하는 코드가 view에 있음

# from django.test import TestCase

# from chats.models import ChatRoom, ChatRoomUser, Message
# from chats.serializers import ChatRoomSerializer
# from users.models import User

# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# class ChatRoomSerializerTest(TestCase):
#     def setUp(self):
#         self.main_user = User.objects.create_user(
#             nickname="서강준",
#             social_provider="google",
#             email="haha@haha.com",
#             profile_image="서강준.jpg",
#         )

#         self.other_user = User.objects.create_user(
#             nickname="아이유",
#             social_provider="google",
#             email="ee@ee.com",
#             profile_image="아이유.png",
#         )
    
#         self.chatroom = ChatRoom.objects.create()
#         ChatRoomUser.objects.create(chatroom=self.chatroom, user=self.main_user)
#         ChatRoomUser.objects.create(chatroom=self.chatroom, user=self.other_user)

#     def test_chat_room_serializer(self):
#         serializer = ChatRoomSerializer(self.chatroom)
#         data = serializer.data

#         self.assertEqual(data["main_user_nickname"], self.main_user.nickname)
#         self.assertEqual(data["other_user_nickname"], self.other_user.nickname)

#     def test_get_latest_message_with_no_messages(self):
#         serializer = ChatRoomSerializer(self.chatroom)

#         self.assertIsNone(serializer.get_latest_message(self.chatroom))
#         self.assertIsNone(serializer.get_latest_message_time(self.chatroom))

#     def test_get_latest_message_with_messages(self):
#         message = Message.objects.create(room=self.chatroom, sender=self.main_user, text="하이!")
#         serializer = ChatRoomSerializer(self.chatroom)

#         self.assertEqual(serializer.get_latest_message(self.chatroom), message.text)
#         self.assertIsNotNone(serializer.get_latest_message_time(self.chatroom))
#         self.assertEqual(serializer.get_latest_message_time(self.chatroom), message.updated_at)

#     def test_get_main_user_nickname(self):
#         serializer = ChatRoomSerializer(self.chatroom)

#         self.assertEqual(serializer.get_main_user_nickname(self.chatroom), self.main_user.nickname)

#     def test_get_other_user_nickname(self):
#         serializer = ChatRoomSerializer(self.chatroom)

#         self.assertEqual(serializer.get_other_user_nickname(self.chatroom), self.other_user.nickname)

#     # def test_get_other_user_profile_image(self):
#     #     serializer = ChatRoomSerializer(self.chat_room)

#     #     self.assertEqual(serializer.get_other_user_profile_image(self.chat_room), self.other_user.profile_image.url)
