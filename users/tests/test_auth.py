from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from users.models import UserProfile

User = get_user_model()


class AuthenticationTests(TestCase):
    def test_signup_hashes_password_and_creates_profile(self):
        response = self.client.post(
            reverse("users:signup"),
            {
                "username": "alice",
                "display_name": "앨리스",
                "password1": "Strong-Test-Password-123!",
                "password2": "Strong-Test-Password-123!",
            },
        )
        self.assertRedirects(response, reverse("users:login"))
        user = User.objects.get(username="alice")
        self.assertNotEqual(user.password, "Strong-Test-Password-123!")
        self.assertTrue(user.check_password("Strong-Test-Password-123!"))
        self.assertEqual(user.profile.display_name, "앨리스")

    def test_duplicate_username_is_rejected(self):
        User.objects.create_user("alice", password="Strong-Test-Password-123!")
        response = self.client.post(
            reverse("users:signup"),
            {
                "username": "alice",
                "display_name": "다른 이름",
                "password1": "Strong-Test-Password-456!",
                "password2": "Strong-Test-Password-456!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="alice").count(), 1)

    def test_blocked_user_cannot_login(self):
        User.objects.create_user(
            "blocked", password="Strong-Test-Password-123!", status=User.Status.BLOCKED
        )
        response = self.client.post(
            reverse("users:login"), {"username": "blocked", "password": "Strong-Test-Password-123!"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_requires_post(self):
        user = User.objects.create_user("alice", password="Strong-Test-Password-123!")
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("users:logout")).status_code, 405)
        self.assertEqual(self.client.post(reverse("users:logout")).status_code, 302)

    def test_mypage_requires_authentication(self):
        response = self.client.get(reverse("users:mypage"))
        self.assertRedirects(response, f"{reverse('users:login')}?next={reverse('users:mypage')}")

    def test_user_can_only_edit_own_profile(self):
        alice = User.objects.create_user("alice", password="Strong-Test-Password-123!")
        alice_profile, _ = UserProfile.objects.get_or_create(
            user=alice, defaults={"display_name": "alice"}
        )
        bob = User.objects.create_user("bob", password="Strong-Test-Password-123!")
        UserProfile.objects.get_or_create(user=bob, defaults={"display_name": "bob"})
        self.client.force_login(alice)
        response = self.client.post(
            reverse("users:profile_edit"),
            {"display_name": "Alice", "bio": "<script>alert(1)</script>"},
        )
        self.assertRedirects(response, reverse("users:mypage"))
        alice_profile.refresh_from_db()
        self.assertEqual(alice_profile.display_name, "Alice")
        bob.refresh_from_db()
        self.assertEqual(bob.profile.display_name, "bob")
        page = self.client.get(reverse("users:mypage"))
        self.assertNotContains(page, "<script>", html=False)
        self.assertContains(page, "&lt;script&gt;")
