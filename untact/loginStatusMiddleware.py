from exhibition.models import UserActivity
from datetime import datetime
from django.conf import settings
import re

class LoginStatusMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print('login status middleware called')
        response = self.get_response(request)
        print('response : ', response)
        if hasattr(self, 'process_request'):
            self.process_request(request)
        return response
    
    def process_request(self, request):
        if not request.user.is_authenticated:
            return
        print('process request in')
        activity = None
        try:
            activity = request.user.useractivity
        except:
            activity = UserActivity()
            activity.user = request.user
            activity.last_activity_date = datetime.now()
            activity.last_activity_ip = request.META['REMOTE_ADDR']
            activity.dnd = False
            activity.save()
            print('activity saved')
            return
        activity.dnd = False
        activity.last_activity_date = datetime.now()
        activity.last_activity_ip = request.META['REMOTE_ADDR']
        activity.save()
        print('activity saved')
