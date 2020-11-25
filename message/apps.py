from django.apps import AppConfig

class MessageConfig(AppConfig):
    name = 'message'
    def ready(self):
        from .models import Invitation
        from exhibition.models import UserWithTitle as User
        from exhibition.models import StatusType
        Invitation.objects.all().delete()
        User.objects.all().update(channel_id="", consumer="", status=StatusType.OFFLINE)