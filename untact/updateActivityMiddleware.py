from exhibition.models import UserWithTitle
import datetime
from django.conf import settings

class UpdateActivityMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if hasattr(self, 'process_request'):
            self.process_request(request)
        return response
    
    def process_request(self, request):
        if not request.user.is_authenticated:
            return
        
        u = request.user.id
        print(u)
        userAct = UserWithTitle.objects.get(id=u)
        print(userAct)
        userAct.last_activity_date = datetime.datetime.now(datetime.timezone.utc)
        userAct.save()
