from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from ..models.user_model import Users

class UserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "email": "testuser@test.com",
            "password": "testpassword",
            "plan": "Enterprise"
        }
        self.user = Users.objects.create(**self.user_data)

    def test_login_should_return_200_when_user_is_valid(self):
        url = reverse("login")
        data = {
            "email": "testuser@test.com",
            "password": "testpassword",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_should_return_401_when_password_is_invalid(self):
        url = reverse("login")
        data = {
            "email": "testuser@test.com",
            "password": "invalidpassword",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_should_return_404_when_user_is_not_found(self):
        url = reverse("login")
        data = {
            "email": "invaliduser@test.com",
            "password": "testpassword",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_login_should_return_400_when_validation_error(self):
        url = reverse("login")
        data = {
            "email": "",
            "password": "",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
