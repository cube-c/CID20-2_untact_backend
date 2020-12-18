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
from django.conf import settings
from .models import Invitation

class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            prev_consumer = await self.update_consumer()
            print(prev_consumer, self.channel_name)
            if prev_consumer:
                await self.channel_layer.send(prev_consumer, {"type": "send_close"})
            await self.accept()
            await self.enter()
            await self.send_sent_invitations_state({})
            await self.send_received_invitations_state({})

    async def disconnect(self, close_code):
        if not self.user.is_anonymous:
            receiver_consumers = await self.leave_all()
            await self.send_received_invitations_state_consumers(receiver_consumers)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        call = text_data_json["type"]
        if call == "leave":
            status, sender_consumers, receiver_consumers = await self.leave_channel()
            if status:
                await self.send(text_data=json.dumps({"type": "leave_success", "info": "You leaved the channel successfully."}))
            else:
                await self.send(text_data=json.dumps({"type": "leave_fail", "info": "You are not in a channel."}))
            await self.send_sent_invitations_state_consumers(sender_consumers)
            await self.send_channel_id_state_consumers(sender_consumers)
            await self.send_received_invitations_state_consumers(receiver_consumers)
        else:
            username = text_data_json["username"]
            other = await self.get_user(username)
            if other == self.user:
                await self.send(text_data=json.dumps({"type": "username_self_fail", "info": "username cannot be yourself"}))
            elif other:
                current_time = datetime.datetime.now(datetime.timezone.utc)
                if call == "invite":
                    status, sender_consumers, receiver_consumers = await self.invite_user(self.user, other, current_time)
                    await self.send_sent_invitations_state_consumers(sender_consumers)
                    await self.send_channel_id_state_consumers(sender_consumers)
                    await self.send_received_invitations_state_consumers(receiver_consumers)
                    if status:
                        await self.send(text_data=json.dumps({"type": "invite_success",
                                        "info": "{}".format(username)}))
                        await self.send_message_consumers(receiver_consumers, self.user, "invited_you")
                    else:
                        await self.send(text_data=json.dumps({"type": "invite_same_channel_fail",
                                        "info": "{}".format(username)}))
                elif call == "accept":
                    status, sender_consumers, receiver_consumers, info = await self.accept_user(other, self.user, current_time)
                    await self.send_sent_invitations_state_consumers(sender_consumers)
                    await self.send_received_invitations_state_consumers(receiver_consumers)
                    await self.send_channel_id_state_consumers(receiver_consumers)
                    if status:
                        await self.send(text_data=json.dumps({"type": "accept_success", "info": info})) #username who invited you
                        await self.send_message_consumers(sender_consumers, self.user, "accepted_you")
                    else:
                        await self.send(text_data=json.dumps({"type": "accept_fail", "info": info})) #already_in_channel, channel_is_full, invitation_not_exist
                elif call == "reject":
                    status, sender_consumers, receiver_consumers = await self.reject_user(other, self.user)
                    await self.send_sent_invitations_state_consumers(sender_consumers)
                    await self.send_received_invitations_state_consumers(receiver_consumers)
                    if status:
                        await self.send(text_data=json.dumps({"type": "reject_success", 
                                        "info": "{}".format(username)}))
                        await self.send_message_consumers(sender_consumers, self.user, "rejected_you")
                    else:
                        await self.send(text_data=json.dumps({"type": "reject_fail",
                                        "info": "invitation_not_exist"}))
                elif call == "cancel":
                    status, sender_consumers, receiver_consumers = await self.reject_user(self.user, other)
                    await self.send_sent_invitations_state_consumers(sender_consumers)
                    await self.send_received_invitations_state_consumers(receiver_consumers)
                    if status:
                        await self.send(text_data=json.dumps({"type": "cancel_success", 
                                        "info": "You canceled the invitation."}))
                        await self.send_message_consumers(sender_consumers, other, "canceled")
                    else:
                        await self.send(text_data=json.dumps({"type": "cancel_fail",
                                        "info": "invitation_not_exist"}))
                else:
                    await self.send(text_data=json.dumps({"type": "type_fail", "info": "Request type is invalid."}))
            else:
                await self.send(text_data=json.dumps({"type": "username_not_exist_fail", 
                                "info": "Cannot find any account associated with that username."}))

    async def send_sent_invitations_state_consumers(self, consumers):
        for consumer in consumers:
            if consumer:
                await self.channel_layer.send(consumer, {"type": "send_sent_invitations_state"})

    async def send_received_invitations_state_consumers(self, consumers):
        for consumer in consumers:
            if consumer:
                await self.channel_layer.send(consumer, {"type": "send_received_invitations_state"})

    async def send_channel_id_state_consumers(self, consumers):
        for consumer in consumers:
            if consumer:
                await self.channel_layer.send(consumer, {"type": "send_channel_id_state"})

    async def send_message_consumers(self, consumers, user, message):
        for consumer in consumers:
            if consumer:
                await self.channel_layer.send(consumer, {"type": "send_message", "user_name": user.username, "user_title": user.title, "message": message})

    async def send_sent_invitations_state(self, event):
        sent_invitations = await self.get_sent_invitations()
        await self.send(text_data=json.dumps({"type": "sent_invitations_state", "invitations": sent_invitations}))

    async def send_received_invitations_state(self, event):
        received_invitations = await self.get_received_invitations()
        await self.send(text_data=json.dumps({"type": "received_invitations_state", "invitations": received_invitations}))

    async def send_channel_id_state(self, event):
        await self.send(text_data=json.dumps({"type": "channel_id_state", "channel_id": self.user.channel_id}))

    async def send_message(self, event):
        await self.send(text_data=json.dumps({"type": "message", "user_name": event["user_name"], "user_title": event["user_title"], "message": event["message"]}))

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
    def get_sent_invitations(self):
        return sorted([{"name": invitation.guest.username, "title": invitation.guest.title,
                        "timestamp": time.mktime(invitation.invited_on.timetuple())}
                        for invitation in Invitation.objects.filter(host=self.user)],
                        key=lambda k: k["timestamp"], reverse=True)

    @database_sync_to_async
    def get_received_invitations(self):
        return sorted([{"name": invitation.host.username, "title": invitation.host.title,
                        "timestamp": time.mktime(invitation.invited_on.timetuple())}
                        for invitation in Invitation.objects.filter(guest=self.user)],
                        key=lambda k: k["timestamp"], reverse=True)\
    
    @database_sync_to_async
    def invite_user(self, host, guest, current_time):
        if host.channel_id and host.channel_id == guest.channel_id:
            return False, [], []
        Invitation.objects.update_or_create(host=host, guest=guest, defaults={"invited_on": current_time})
        if not host.channel_id:
            host.channel_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
            host.save()
        return True, [host.consumer], [guest.consumer]

    @database_sync_to_async
    def accept_user(self, host, guest, current_time):
        invitation = Invitation.objects.filter(host=host, guest=guest)
        if guest.channel_id:
            return False, [], [], "already_in_channel"
        if invitation.exists():
            with transaction.atomic():
                if User.objects.filter(channel_id=host.channel_id).count() >= 7:
                    return False, [], [], "channel_is_full"
                Invitation.objects.filter(host__channel_id=host.channel_id, guest=guest).delete()
                guest.channel_id = host.channel_id
                guest.save()
            return True, [host.consumer], [guest.consumer], "{}".format(host.username)
        return False, [], [], "invitation_not_exist"
    
    @database_sync_to_async
    def reject_user(self, host, guest):
        invitation = Invitation.objects.filter(host=host, guest=guest)
        if invitation.exists():
            invitation.delete()
            return True, [host.consumer], [guest.consumer]
        return False, [], []

    @database_sync_to_async
    def leave_channel(self):
        if self.user.channel_id:
            invitations = Invitation.objects.filter(host=self.user)
            consumers_invitation = list(invitations.values_list("guest__consumer", flat=True))
            consumers_invitation.append(self.user.consumer)
            invitations.delete()
            self.user.channel_id = ''
            self.user.save()
            return True, [self.user.consumer], consumers_invitation
        return False, [], [] 
    
    @database_sync_to_async
    def enter(self):
        self.user.is_online = True
        self.user.save()

    @database_sync_to_async
    def leave_all(self):
        invitations = Invitation.objects.filter(host=self.user)
        consumers_invitation = list(invitations.values_list("guest__consumer", flat=True))
        invitations.delete()
        self.user.channel_id = ""
        self.user.consumer = ""
        self.user.is_online = False 
        self.user.save()
        return consumers_invitation
