import json
import time
import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.auth import login
from channels.db import database_sync_to_async
from exhibition.models import UserWithTitle
from django.db import transaction
from .models import Invitation

class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_group_name = "message"

        if self.user.is_anonymous:
            await self.close()
        else:
            await self.channel_layer.group_add(
                self.room_group_name, self.channel_name
            )
            await self.accept()
            invitations = await self.get_invitations(self.user)
            for invitation in invitations:
                timestamp = time.mktime(invitation["invited_on"].timetuple())
                host = invitation["host"].username
                guest = invitation["guest"].username
                await self.send(text_data=json.dumps({"status": True, 
                    "info": {"host": host, "guest": guest, "timestamp": timestamp}}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        username = text_data_json["username"]
        guest = await self.get_user(username)

        if guest == self.user:
            await self.send(text_data=json.dumps({"status": False, 
                "info": "You cannot invite yourself"}))
        elif guest:
            invited_on = datetime.datetime.now(datetime.timezone.utc)
            timestamp = time.mktime(invited_on.timetuple())
            await self.invite_user(self.user, guest, invited_on)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "invitation",
                    "host": self.user.username,
                    "guest": username,
                    "timestamp": timestamp 
                }
            )
        else:
            await self.send(text_data=json.dumps({"status": False, 
                "info": "Cannot find any account associated with that username"}))


    async def invitation(self, event):
        host = event["host"]
        guest = event["guest"]
        timestamp = event["timestamp"]
        if guest == self.user.username or host == self.user.username:
            await self.send(text_data=json.dumps({"status": True, 
                "info": {"host": host, "guest": guest, "timestamp": timestamp}}))
    
    @database_sync_to_async
    def get_user(self, username):
        try:
            user = UserWithTitle.objects.get(username=username)
            return user 
        except UserWithTitle.DoesNotExist:
            return None
    
    @database_sync_to_async
    def invite_user(self, host, guest, invited_on):
        invitation, _ = Invitation.objects.get_or_create(host=host, guest=guest, defaults={"invited_on": invited_on})
        return invitation
    
    @database_sync_to_async
    def get_invitations(self, guest):
        return [{"host": invitation.host, "guest": invitation.guest, "invited_on": invitation.invited_on}
                for invitation in Invitation.objects.filter(guest=guest)]