from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse

from chat.models import Conversation, Message
from chat.routing import websocket_urlpatterns
from chat.services import get_global_conversation, get_or_create_direct_conversation

User = get_user_model()
IN_MEMORY_CHANNELS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}


class ChatHttpTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="Test-Password-123!")
        self.bob = User.objects.create_user("bob", password="Test-Password-123!")
        self.mallory = User.objects.create_user("mallory", password="Test-Password-123!")

    def test_global_chat_is_single_and_requires_authentication(self):
        self.assertEqual(self.client.get(reverse("chat:global")).status_code, 302)
        first = get_global_conversation(self.alice)
        second = get_global_conversation(self.bob)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(first.memberships.count(), 2)

    def test_direct_chat_is_canonical_and_has_exact_members(self):
        first = get_or_create_direct_conversation(self.alice, self.bob)
        second = get_or_create_direct_conversation(self.bob, self.alice)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(
            set(first.memberships.values_list("user_id", flat=True)),
            {self.alice.pk, self.bob.pk},
        )

    def test_direct_start_requires_post_and_outsider_gets_403(self):
        self.client.force_login(self.alice)
        url = reverse("chat:direct_start", args=[self.bob.username])
        self.assertEqual(self.client.get(url).status_code, 405)
        response = self.client.post(url)
        conversation = Conversation.objects.get(kind=Conversation.Kind.DIRECT)
        self.assertRedirects(response, reverse("chat:detail", args=[conversation.pk]))
        self.client.force_login(self.mallory)
        self.assertEqual(
            self.client.get(reverse("chat:detail", args=[conversation.pk])).status_code,
            403,
        )

    def test_hidden_messages_are_not_rendered_and_xss_is_escaped(self):
        conversation = get_or_create_direct_conversation(self.alice, self.bob)
        Message.objects.create(
            conversation=conversation,
            sender=self.alice,
            content="<script>alert(1)</script>",
        )
        Message.objects.create(
            conversation=conversation,
            sender=self.alice,
            content="관리자 숨김",
            status=Message.Status.HIDDEN,
        )
        self.client.force_login(self.bob)
        response = self.client.get(reverse("chat:detail", args=[conversation.pk]))
        self.assertNotContains(response, "<script>alert(1)</script>", html=False)
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "관리자 숨김")

    def test_blocked_user_cannot_create_direct_chat(self):
        self.bob.status = User.Status.BLOCKED
        self.bob.save(update_fields=("status",))
        self.client.force_login(self.alice)
        response = self.client.post(reverse("chat:direct_start", args=[self.bob.username]))
        self.assertEqual(response.status_code, 404)


@override_settings(CHANNEL_LAYERS=IN_MEMORY_CHANNELS, CHAT_MESSAGES_PER_MINUTE=2)
class ChatWebSocketTests(TransactionTestCase):
    def setUp(self):
        self.alice = User.objects.create_user("ws-alice", password="Test-Password-123!")
        self.bob = User.objects.create_user("ws-bob", password="Test-Password-123!")
        self.mallory = User.objects.create_user("ws-mallory", password="Test-Password-123!")
        self.conversation = get_or_create_direct_conversation(self.alice, self.bob)

    def communicator(self, user):
        communicator = WebsocketCommunicator(
            URLRouter(websocket_urlpatterns), f"/ws/chat/{self.conversation.pk}/"
        )
        communicator.scope["user"] = user
        return communicator

    async def test_unauthenticated_and_nonmember_connections_are_rejected(self):
        anonymous = self.communicator(AnonymousUser())
        connected, code = await anonymous.connect()
        self.assertFalse(connected)
        self.assertEqual(code, 4401)
        outsider = self.communicator(self.mallory)
        connected, code = await outsider.connect()
        self.assertFalse(connected)
        self.assertEqual(code, 4403)

    async def test_members_exchange_persisted_message(self):
        alice = self.communicator(self.alice)
        bob = self.communicator(self.bob)
        self.assertTrue((await alice.connect())[0])
        self.assertTrue((await bob.connect())[0])
        await alice.send_json_to({"message": "안전한 메시지"})
        alice_event = await alice.receive_json_from()
        bob_event = await bob.receive_json_from()
        self.assertEqual(alice_event["message"], "안전한 메시지")
        self.assertEqual(bob_event["sender"], self.alice.profile.display_name)
        self.assertEqual(await Message.objects.acount(), 1)
        await alice.disconnect()
        await bob.disconnect()

    async def test_user_blocked_after_connect_is_disconnected_before_receiving(self):
        alice = self.communicator(self.alice)
        bob = self.communicator(self.bob)
        self.assertTrue((await alice.connect())[0])
        self.assertTrue((await bob.connect())[0])
        await User.objects.filter(pk=self.bob.pk).aupdate(status=User.Status.BLOCKED)
        await alice.send_json_to({"message": "차단 후 메시지"})
        self.assertEqual((await alice.receive_json_from())["message"], "차단 후 메시지")
        close_event = await bob.receive_output()
        self.assertEqual(close_event["type"], "websocket.close")
        self.assertEqual(close_event["code"], 4403)
        await alice.disconnect()

    async def test_invalid_length_and_rate_limit(self):
        communicator = self.communicator(self.alice)
        self.assertTrue((await communicator.connect())[0])
        await communicator.send_json_to({"message": ""})
        self.assertEqual((await communicator.receive_json_from())["error"], "invalid_length")
        for text in ("one", "two"):
            await communicator.send_json_to({"message": text})
            self.assertEqual((await communicator.receive_json_from())["message"], text)
        await communicator.send_json_to({"message": "three"})
        self.assertEqual((await communicator.receive_json_from())["error"], "rate_limited")
        await communicator.disconnect()
