from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import TestCase, override_settings
from django.urls import reverse

from chat.services import get_or_create_direct_conversation

User = get_user_model()


@override_settings(DEBUG=False)
class BrowserSecurityTests(TestCase):
    def test_security_headers_apply_to_html_responses(self):
        response = self.client.get(reverse("products:list"))
        policy = response.headers["Content-Security-Policy"]
        script_policy = next(
            directive
            for directive in policy.split(";")
            if directive.strip().startswith("script-src")
        )
        style_policy = next(
            directive
            for directive in policy.split(";")
            if directive.strip().startswith("style-src")
        )
        self.assertIn("object-src 'none'", policy)
        self.assertIn("frame-ancestors 'none'", policy)
        self.assertNotIn("'unsafe-inline'", script_policy)
        self.assertNotIn("'unsafe-inline'", style_policy)
        self.assertEqual(
            response.headers["Permissions-Policy"],
            "camera=(), microphone=(), geolocation=(), payment=()",
        )

    def test_static_security_assets_are_discoverable_for_collectstatic(self):
        self.assertIsNotNone(finders.find("chat/chat.js"))
        self.assertIsNotNone(finders.find("css/app.css"))

    def test_chat_uses_external_script_compatible_with_csp(self):
        alice = User.objects.create_user("csp-alice", password="Test-Password-123!")
        bob = User.objects.create_user("csp-bob", password="Test-Password-123!")
        conversation = get_or_create_direct_conversation(alice, bob)
        self.client.force_login(alice)
        response = self.client.get(reverse("chat:detail", args=[conversation.pk]))
        self.assertContains(response, "/static/chat/chat.js")
        self.assertNotContains(response, "new WebSocket", html=False)
        self.assertNotContains(response, "<script>", html=False)

    def test_custom_403_and_404_pages_hide_internal_details(self):
        user = User.objects.create_user("regular", password="Test-Password-123!")
        self.client.force_login(user)
        forbidden = self.client.get(reverse("moderation:dashboard"))
        missing = self.client.get("/does-not-exist-for-security-test/")
        self.assertContains(forbidden, "접근할 수 없습니다", status_code=403)
        self.assertContains(missing, "페이지를 찾을 수 없습니다", status_code=404)
        self.assertNotContains(missing, "Traceback", status_code=404)
