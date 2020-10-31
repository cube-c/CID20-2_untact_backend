from exhibition.models import UserActivity, UserWithTitle
import datetime
from django.conf import settings
import re

class LoginStatusMiddleware(object):
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
        activity = None
        
        try:
            activity = request.user.useractivity
        except:
            print('user activity doesn\'t exist : make new activity')
            activity = UserActivity()
            activity.user = request.user
            activity.last_activity_date = datetime.datetime.now(datetime.timezone.utc)
            activity.last_activity_ip = request.META['REMOTE_ADDR']
            activity.dnd = False
            activity.save()
            return
        activity.dnd = False
        activity.last_activity_date = datetime.datetime.now(datetime.timezone.utc)
        activity.last_activity_ip = request.META['REMOTE_ADDR']
        activity.save()
