import json
from json import JSONDecodeError
from django.contrib.auth import authenticate, login
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
import datetime
from .models import Exhibit
from .models import Position
from .models import UserActivity

def auth_func(func):
    def wrapper_function(*args, **kwargs):
        if (args[0].user.is_authenticated):
            return func(*args, **kwargs)
        return HttpResponse(status=401)
    return wrapper_function

@auth_func
def api_exhibit(request):
    if request.method == 'GET':
        exhibit_position_id_list = [exhibit['position_id'] for exhibit in Exhibit.objects.all().values()]
        exhibit_position_list = [list(Position.objects.filter(position_id=position_id).values())[0] for position_id in exhibit_position_id_list]
        exhibit_all_list = [{**exhibit, **position} for exhibit, position in zip(Exhibit.objects.all().values(), exhibit_position_list)]
        return JsonResponse(exhibit_all_list, safe=False)
    return HttpResponseNotAllowed(['GET'])

@auth_func
def api_userStatus(request):
    if request.method == 'GET':
        status_lastActivityDate = [userActivity['last_activity_date'] for userActivity in UserActivity.objects.all().values()]
        status_isActivated = []
        for time in status_lastActivityDate:
            if datetime.datetime.now(datetime.timezone.utc) - time > datetime.timedelta(seconds = 30):
                status_isActivated.append({'currLoginStatus' : False})
            else:
                status_isActivated.append({'currLoginStatus' : False})
        status_list = [{**userActivity, **currLoginStatus} for userActivity, currLoginStatus in zip(UserActivity.objects.values(), status_isActivated)]
        return JsonResponse(status_list, safe=False)
    return HttpResponseNotAllowed(['GET'])


# @auth_func
# def api_position(request, position_id):
#     if request.method == 'GET':
#         position_data = list(Position.objects.filter(position_id=position_id).values('posx', 'posy', 'posz', 'roty'))
#         return JsonResponse(position_data, safe=False)
#     return HttpResponseNotAllowed(['GET'])

def api_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse(status=204)
        return HttpResponse(status=401)
    return HttpResponseNotAllowed(['POST'])

@ensure_csrf_cookie
def api_token(request):
    if request.method == 'GET':
        return HttpResponse(status=204)
    return HttpResponseNotAllowed(['GET'])
