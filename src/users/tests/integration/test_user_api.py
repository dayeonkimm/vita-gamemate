from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User


class UserProfileAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            nickname="testuser",
            email="testuser@example.com",
            is_mate=False,
        )
        self.url = reverse("user-profile", kwargs={"user_id": self.user.id})

    def test_get_user_profile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nickname"], "testuser")
        self.assertEqual(response.data["email"], "testuser@example.com")

    def test_get_nonexistent_user(self):
        url = reverse("user-profile", kwargs={"user_id": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_mate_profile(self):
        mate = User.objects.create(
            nickname="mateuser",
            email="mate@example.com",
            social_provider="google",
            is_mate=True,
        )
        url = reverse("user-profile", kwargs={"user_id": mate.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, dict))
        self.assertEqual(response.data["is_mate"], True)


class UserMeAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(nickname="testuser", email="testuser@example.com")
        self.access_token = str(TokenObtainPairSerializer.get_token(self.user).access_token)
        self.url = reverse("user-me")

    def test_get_own_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nickname"], "testuser")
        self.assertEqual(response.data["email"], "testuser@example.com")

    def test_get_profile_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        data = {"nickname": "up", "description": "This is an updated description"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nickname"], "up")
        self.assertEqual(response.data["description"], "This is an updated description")

    def test_update_profile_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        data = {"email": "invalid_email"}
        response = self.client.patch(self.url, data)
        self.assertNotEqual(response.data.get("email"), "invalid_email")
