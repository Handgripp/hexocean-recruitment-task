import tempfile
from datetime import datetime, timedelta

import jwt
from decouple import config
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from ..models.user_model import Users
from ..models.image_model import Images
from django.urls import reverse


class UploadImageTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "email": "testuser@test.com",
            "password": "testpassword",
            "plan": "Enterprise"
        }
        self.user = Users.objects.create(**self.user_data)

    def test_upload_image_with_auth_should_return_201_when_user_is_valid(self):
        url = reverse("images/upload")
        file_path = "image.png"
        data = {
            "image": open(file_path, "rb"),
        }

        login_url = reverse("login")
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        }
        login_response = self.client.post(login_url, login_data, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        access_token = login_response.data["access"]

        response = self.client.post(url, data, format="multipart", headers={"Authorization": access_token})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("image_links", response.data)

    def test_upload_image_with_auth_should_return_401_when_user_is_invalid(self):
        url = reverse("images/upload")
        with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
            data = {
                "image": temp_file
            }

            login_url = reverse("login")
            login_data = {
                "email": "testuser@test.com",
                "password": "invalidpassword",
            }
            login_response = self.client.post(login_url, login_data, format="json")
            self.assertEqual(login_response.status_code, status.HTTP_401_UNAUTHORIZED)

            self.assertNotIn("access", login_response.data)

            response = self.client.post(url, data, format="multipart", headers={"Authorization": "access"})
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertNotIn("image_links", response.data)

    def test_upload_image_with_auth_should_return_400_when_file_format_was_incorrect(self):
        url = reverse("images/upload")

        with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
            data = {
                "image": temp_file
            }

            login_url = reverse("login")
            login_data = {
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            }
            login_response = self.client.post(login_url, login_data, format="json")
            self.assertEqual(login_response.status_code, status.HTTP_200_OK)
            access_token = login_response.data["access"]

            response = self.client.post(url, data, format="multipart", headers={"Authorization": access_token})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("error", response.data)
            self.assertEqual(response.data["error"], "Incorrect file format")

    def test_upload_image_with_auth_should_return_404_when_no_file(self):
        url = reverse("images/upload")
        data = {}

        login_url = reverse("login")
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        }
        login_response = self.client.post(login_url, login_data, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        access_token = login_response.data["access"]

        response = self.client.post(url, data, format="multipart", headers={"Authorization": access_token})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "File not found")


class ShowImageTestCase(TestCase):
    def setUp(self):
        self.user = Users.objects.create(
            email="testuser@test.com",
            password="testpassword",
            plan="Enterprise"
        )

        self.image = Images.objects.create(
            user_id=self.user,
            path="image.png",
            format="png"
        )
        self.signing_key = config('SIGNING_KEY')

    def test_show_image_should_return_200_when_token_is_valid(self):
        expiration_time = datetime.utcnow() + timedelta(hours=1)
        token = jwt.encode({"exp": expiration_time.timestamp()}, self.signing_key, algorithm="HS256")

        url = reverse("images/image_id", kwargs={"image_id": self.image.id})
        query_params = {"expires_token": token}

        response = self.client.get(url, query_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_show_image_should_return_401_when_token_is_expired(self):
        expiration_time = datetime.utcnow() - timedelta(hours=1)
        token = jwt.encode({"exp": expiration_time.timestamp()}, self.signing_key, algorithm="HS256")

        url = reverse("images/image_id", kwargs={"image_id": self.image.id})
        query_params = {"expires_token": token}

        response = self.client.get(url, query_params)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

