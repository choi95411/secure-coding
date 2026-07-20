from channels.testing import WebsocketCommunicator
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TransactionTestCase, override_settings

from chat.services import get_or_create_direct_conversation
from config.asgi import application

User = get_user_model()
IN_MEMORY_CHANNELS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}


@override_settings(CHANNEL_LAYERS=IN_MEMORY_CHANNELS)
class AsgiSessionAuthenticationTests(TransactionTestCase):
    def setUp(self):
        self.alice = User.objects.create_user("asgi-alice", password="Test-Password-123!")
        self.bob = User.objects.create_user("asgi-bob", password="Test-Password-123!")
        self.conversation = get_or_create_direct_conversation(self.alice, self.bob)
        client = Client()
        client.force_login(self.alice)
        self.session_cookie = client.cookies[settings.SESSION_COOKIE_NAME].value

    async def test_real_asgi_stack_authenticates_session_cookie(self):
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{self.conversation.pk}/",
            headers=[
                (b"origin", b"http://testserver"),
                (
                    b"cookie",
                    f"{settings.SESSION_COOKIE_NAME}={self.session_cookie}".encode(),
                ),
            ],
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_real_asgi_stack_rejects_untrusted_origin(self):
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{self.conversation.pk}/",
            headers=[
                (b"origin", b"https://evil.example"),
                (
                    b"cookie",
                    f"{settings.SESSION_COOKIE_NAME}={self.session_cookie}".encode(),
                ),
            ],
        )
        connected, _ = await communicator.connect()
        self.assertFalse(connected)
