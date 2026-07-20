from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from security_controls.models import LoginThrottle

User = get_user_model()


@override_settings(LOGIN_MAX_FAILURES=2, LOGIN_LOCK_SECONDS=900)
class LoginThrottleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", password="Correct-Password-123!")
        self.url = reverse("users:login")

    def test_repeated_failures_lock_even_correct_password(self):
        for _ in range(2):
            response = self.client.post(
                self.url,
                {"username": "alice", "password": "wrong-password"},
                REMOTE_ADDR="192.0.2.10",
            )
            self.assertEqual(response.status_code, 200)
        response = self.client.post(
            self.url,
            {"username": "alice", "password": "Correct-Password-123!"},
            REMOTE_ADDR="192.0.2.10",
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_success_clears_previous_failures(self):
        self.client.post(
            self.url,
            {"username": "alice", "password": "wrong-password"},
            REMOTE_ADDR="192.0.2.11",
        )
        response = self.client.post(
            self.url,
            {"username": "alice", "password": "Correct-Password-123!"},
            REMOTE_ADDR="192.0.2.11",
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(LoginThrottle.objects.exists())

    def test_identifier_does_not_store_username_or_ip(self):
        self.client.post(
            self.url,
            {"username": "alice", "password": "wrong-password"},
            REMOTE_ADDR="192.0.2.12",
        )
        identifier = LoginThrottle.objects.get().identifier_hash
        self.assertNotIn("alice", identifier)
        self.assertNotIn("192.0.2.12", identifier)
