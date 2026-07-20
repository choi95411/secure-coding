from datetime import timedelta

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import Conversation, Message
from .services import can_access_conversation


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["pk"]
        self.group_name = f"chat_{self.conversation_id}"
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return
        if not await self._authorized(user.pk):
            await self.close(code=4403)
            return
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if not await self._authorized(self.scope["user"].pk):
            await self.close(code=4403)
            return
        text = content.get("message")
        if not isinstance(text, str):
            await self.send_json({"error": "invalid_message"})
            return
        text = text.strip()
        if not text or len(text) > 1000:
            await self.send_json({"error": "invalid_length"})
            return
        result = await self._create_message(self.scope["user"].pk, text)
        if result is None:
            await self.send_json({"error": "rate_limited"})
            return
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "id": result[0],
                "sender": result[1],
                "message": text,
                "created_at": result[2],
            },
        )

    async def chat_message(self, event):
        if not await self._authorized(self.scope["user"].pk):
            await self.close(code=4403)
            return
        await self.send_json(
            {
                "id": event["id"],
                "sender": event["sender"],
                "message": event["message"],
                "created_at": event["created_at"],
            }
        )

    @database_sync_to_async
    def _authorized(self, user_id):
        from users.models import User

        try:
            user = User.objects.get(pk=user_id)
            conversation = Conversation.objects.get(pk=self.conversation_id)
        except (User.DoesNotExist, Conversation.DoesNotExist):
            return False
        return can_access_conversation(user, conversation)

    @database_sync_to_async
    @transaction.atomic
    def _create_message(self, user_id, text):
        from users.models import User

        user = User.objects.select_for_update().get(pk=user_id)
        conversation = Conversation.objects.get(pk=self.conversation_id)
        if not can_access_conversation(user, conversation):
            return None
        since = timezone.now() - timedelta(seconds=60)
        limit = int(getattr(settings, "CHAT_MESSAGES_PER_MINUTE", 20))
        recent = Message.objects.filter(sender=user, created_at__gte=since).count()
        if recent >= limit:
            return None
        message = Message.objects.create(conversation=conversation, sender=user, content=text)
        Conversation.objects.filter(pk=conversation.pk).update(updated_at=timezone.now())
        display_name = getattr(getattr(user, "profile", None), "display_name", user.username)
        return message.pk, display_name, message.created_at.isoformat()
