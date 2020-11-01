from exhibition.models import StatusType, UserWithTitle
import datetime
from django.conf import settings

class UpdateActivityMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(self, 'process_request'):
            self.process_request(request)
        response = self.get_response(request)
        return response
    
    def process_request(self, request):
        if not request.user.is_authenticated:
            return
        user_id = request.user.id
        userAct = UserWithTitle.objects.get(id = user_id)
        userAct.last_activity_date = datetime.datetime.now(datetime.timezone.utc)
        if userAct.status != StatusType.DND:
            userAct.status = StatusType.ONLINE
        userAct.save()
