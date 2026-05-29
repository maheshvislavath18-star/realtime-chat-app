import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from django.contrib.auth.models import User
from .models import Room, Message

# 👥 ONLINE USERS (RAM STORE)
online_users = {}


class ChatConsumer(AsyncWebsocketConsumer):

    # ================= CONNECT =================
    async def connect(self):

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # add online user
        online_users.setdefault(self.room_name, set())
        online_users[self.room_name].add(self.user.username)

        await self.broadcast_users()

        # user join event
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_activity",
                "event": "join",
                "username": self.user.username,
            }
        )

        # send history
        messages = await self.get_messages()

        await self.send(text_data=json.dumps({
            "type": "history",
            "messages": messages
        }))

    # ================= DISCONNECT =================
    async def disconnect(self, close_code):

        if hasattr(self, "room_name"):
            if self.room_name in online_users:
                online_users[self.room_name].discard(self.user.username)

        await self.broadcast_users()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_activity",
                "event": "leave",
                "username": self.user.username,
            }
        )

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # ================= RECEIVE =================
    async def receive(self, text_data):

        data = json.loads(text_data)

        msg_type = data.get("type")
        username = self.user.username   # 🔥 FIX (IMPORTANT)
        message = data.get("message")
        image = data.get("image")
        message_id = data.get("message_id")

        # ================= TYPING =================
        if msg_type == "typing":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_event",
                    "username": username
                }
            )
            return

        # ================= SEEN =================
        if msg_type == "seen" and message_id:
            await self.mark_message_seen(message_id)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "message_seen",
                    "message_id": message_id
                }
            )
            return

        # ================= CHAT =================
        if message or image:

            user = await self.get_user(username)
            room = await self.get_room(self.room_name)

            msg_obj = await self.save_message(
                user,
                room,
                message,
                image
            )

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": msg_obj.content,
                    "image": msg_obj.image.url if msg_obj.image else None,
                    "username": username,
                    "created_at": str(msg_obj.created_at),
                    "message_id": msg_obj.id,
                    "is_seen": msg_obj.is_seen
                }
            )

    # ================= EVENTS =================

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat",
            "message": event["message"],
            "image": event["image"],
            "username": event["username"],
            "created_at": event["created_at"],
            "message_id": event["message_id"],
            "is_seen": event["is_seen"]
        }))

    async def typing_event(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing",
            "username": event["username"]
        }))

    async def user_activity(self, event):
        await self.send(text_data=json.dumps({
            "type": "user_activity",
            "event": event["event"],
            "username": event["username"]
        }))

    async def online_users(self, event):
        await self.send(text_data=json.dumps({
            "type": "online_users",
            "users": event["users"]
        }))

    async def message_seen(self, event):
        await self.send(text_data=json.dumps({
            "type": "seen",
            "message_id": event["message_id"]
        }))

    # ================= ONLINE USERS =================

    async def broadcast_users(self):
        users = list(online_users.get(self.room_name, []))

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "online_users",
                "users": users
            }
        )

    # ================= DB =================

    @database_sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @database_sync_to_async
    def get_room(self, room_name):
        return Room.objects.get(name=room_name)

    @database_sync_to_async
    def save_message(self, user, room, message, image=None):
        return Message.objects.create(
            user=user,
            room=room,
            content=message or "",
            image=image
        )

    @database_sync_to_async
    def mark_message_seen(self, message_id):
        try:
            msg = Message.objects.get(id=message_id)
            msg.is_seen = True
            msg.save()
        except Message.DoesNotExist:
            pass

    @database_sync_to_async
    def get_messages(self):
        room = Room.objects.get(name=self.room_name)

        messages = Message.objects.filter(room=room).order_by("created_at")

        return [
            {
                "id": m.id,
                "username": m.user.username,
                "message": m.content,
                "image": m.image.url if m.image else None,
                "created_at": str(m.created_at),
                "is_seen": m.is_seen
            }
            for m in messages
        ]