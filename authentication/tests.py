from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class AuthenticationTests(APITestCase):
    def test_register_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "email": "member@example.com",
                "password": "strongpassword123",
                "name": "Test Member",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["success"])
        self.assertEqual(User.objects.count(), 1)

    def test_login_user(self):
        User.objects.create_user(
            email="member@example.com",
            password="strongpassword123",
            name="Test Member",
        )

        response = self.client.post(
            reverse("login"),
            {
                "email": "member@example.com",
                "password": "strongpassword123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_me_requires_authentication(self):
        response = self.client.get(reverse("me"))
        self.assertEqual(response.status_code, 401)

    def test_me_returns_current_user(self):
        user = User.objects.create_user(
            email="member@example.com",
            password="strongpassword123",
            name="Test Member",
        )

        self.client.force_authenticate(user=user)

        response = self.client.get(reverse("me"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["email"], user.email)

    def test_update_profile(self):
        user = User.objects.create_user(
            email="member@example.com",
            password="strongpassword123",
            name="Test Member",
        )

        self.client.force_authenticate(user=user)

        response = self.client.put(
            reverse("me"),
            {
                "name": "Updated Name",
                "phone": "09123456789",
                "telegram_username": "@updated_user",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        user.refresh_from_db()

        self.assertEqual(user.name, "Updated Name")
        self.assertEqual(user.phone, "09123456789")
        self.assertEqual(user.telegram_username, "@updated_user")