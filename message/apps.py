from django.apps import AppConfig

class MessageConfig(AppConfig):
    name = 'message'
    def ready(self):
        from .models import Invitation
        from exhibition.models import UserWithTitle as User
        Invitation.objects.all().delete()
        User.objects.all().update(channel_id="", consumer="", is_online=False)