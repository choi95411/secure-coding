import os
from unittest import skipUnless

from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from chat.routing import websocket_urlpatterns
from chat.services import get_or_create_direct_conversation

User = get_user_model()


@skipUnless(os.getenv("RUN_REDIS_TESTS") == "1", "requires explicit Redis integration environment")
class RedisChannelLayerIntegrationTests(TransactionTestCase):
    def setUp(self):
        self.alice = User.objects.create_user("redis-alice", password="Test-Password-123!")
        self.bob = User.objects.create_user("redis-bob", password="Test-Password-123!")
        self.conversation = get_or_create_direct_conversation(self.alice, self.bob)

    def communicator(self, user):
        communicator = WebsocketCommunicator(
            URLRouter(websocket_urlpatterns), f"/ws/chat/{self.conversation.pk}/"
        )
        communicator.scope["user"] = user
        return communicator

    async def test_redis_broadcasts_between_two_authenticated_members(self):
        alice = self.communicator(self.alice)
        bob = self.communicator(self.bob)
        self.assertTrue((await alice.connect())[0])
        self.assertTrue((await bob.connect())[0])
        await alice.send_json_to({"message": "Redis 실시간 메시지"})
        self.assertEqual((await alice.receive_json_from())["message"], "Redis 실시간 메시지")
        self.assertEqual((await bob.receive_json_from())["message"], "Redis 실시간 메시지")
        await alice.disconnect()
        await bob.disconnect()
