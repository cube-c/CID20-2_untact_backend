import json
import time
import string
import random
import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.auth import login
from channels.db import database_sync_to_async
from exhibition.models import UserWithTitle as User
from django.db import transaction
from .models import Invitation

class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
        else:
            prev_consumer = await self.update_consumer()
            if prev_consumer:
                await self.channel_layer.send(prev_consumer, {"type": "send_close"})
            await self.accept()
            await self.send_state({})

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        call = text_data_json["type"]
        if call == "leave":
            status, consumers = await self.leave_channel()
            if status:
                await self.send(text_data=json.dumps({"type": "success", "info": "You leaved the channel successfully."}))
            else:
                await self.send(text_data=json.dumps({"type": "fail", "info": "You are not in a channel."}))
            await self.send_state_consumers(consumers)
        else:
            username = text_data_json["username"]
            other = await self.get_user(username)
            if other == self.user:
                await self.send(text_data=json.dumps({"type": "fail", "info": "You cannot send to yourself."}))
            elif other:
                if call == "invite":
                    invited_on = datetime.datetime.now(datetime.timezone.utc)
                    status, consumers = await self.invite_user(self.user, other, invited_on)
                    await self.send_state_consumers(consumers)
                    if status:
                        await self.send(text_data=json.dumps({"type": "success",
                                        "info": "You invited {}.".format(username)}))
                    else:
                        await self.send(text_data=json.dumps({"type": "fail",
                                        "info": "Request is invalid"}))
                elif call == "accept":
                    status, consumers = await self.accept_user(other, self.user)
                    await self.send_state_consumers(consumers)
                    if status:
                        await self.send(text_data=json.dumps({"type": "success", 
                                        "info": "You accepted the invite of {}.".format(username)}))
                    else:
                        await self.send(text_data=json.dumps({"type": "fail",
                                        "info": "Request is invalid"}))
                elif call == "reject":
                    status, consumers = await self.reject_user(other, self.user)
                    await self.send_state_consumers(consumers)
                    if status:
                        await self.send(text_data=json.dumps({"type": "success", 
                                        "info": "You rejected the invite of {}.".format(username)}))
                    else:
                        await self.send(text_data=json.dumps({"type": "fail",
                                        "info": "Request is invalid"}))
                else:
                    await self.send(text_data=json.dumps({"type": "fail", "info": "Request is invalid."}))
            else:
                await self.send(text_data=json.dumps({"type": "fail", 
                                "info": "Cannot find any account associated with that username."}))
    
    async def send_state_consumers(self, consumers):
        for consumer in consumers:
            if consumer:
                await self.channel_layer.send(consumer, {"type": "send_state"})

    async def send_state(self, event):
        invitations = await self.get_invitations()
        await self.send(text_data=json.dumps({"type": "state", "channel_id": self.user.channel_id, "invitations": invitations}))

    async def send_close(self, event):
        await self.close()
    
    @database_sync_to_async
    def update_consumer(self):
        prev_consumer = self.user.consumer
        self.user.consumer = self.channel_name
        self.user.save()
        return prev_consumer

    @database_sync_to_async
    def get_user(self, username):
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_invitations(self):
        return [{"username": invitation.host.username, "timestamp": time.mktime(invitation.invited_on.timetuple())}
                for invitation in Invitation.objects.filter(guest=self.user)]
    
    @database_sync_to_async
    def invite_user(self, host, guest, invited_on):
        if host.channel_id and host.channel_id == guest.channel_id:
            return False, []
        Invitation.objects.update_or_create(host=host, guest=guest, defaults={"invited_on": invited_on})
        if not host.channel_id:
            host.channel_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
            host.save()
            return True, [host.consumer, guest.consumer]
        return True, [guest.consumer]

    @database_sync_to_async
    def accept_user(self, host, guest):
        invitation = Invitation.objects.filter(host=host, guest=guest)
        if invitation.exists() and not guest.channel_id:
            with transaction.atomic():
                Invitation.objects.filter(host__channel_id=host.channel_id, guest=guest).delete()
                guest.channel_id = host.channel_id
                guest.save()
            return True, [guest.consumer]
        return False, []
    
    @database_sync_to_async
    def reject_user(self, host, guest):
        invitation = Invitation.objects.filter(host=host, guest=guest)
        if invitation.exists():
            invitation.delete()
            return True, [guest.consumer]
        return False, []

    @database_sync_to_async
    def leave_channel(self):
        if self.user.channel_id:
            invitations = Invitation.objects.filter(host=self.user)
            consumers_invitation = list(invitations.values_list("guest__consumer", flat=True))
            consumers_invitation.append(self.user.consumer)
            invitations.delete()
            self.user.channel_id = ''
            self.user.save()
            return True, consumers_invitation
        return False, [] 
