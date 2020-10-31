import json
import datetime
from json import JSONDecodeError
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Exhibit, Position, UserWithTitle, UserActivity

def auth_func(func):
    def wrapper_function(*args, **kwargs):
        if (args[0].user.is_authenticated):
            return func(*args, **kwargs)
        return HttpResponse(status=401)
    return wrapper_function

def api_exhibit(request):
    if request.method == 'GET':
        exhibit_query = Exhibit.objects.filter(position_id__isnull=False).select_related('position')
        exhibit_list = [exhibit.data() for exhibit in exhibit_query]
        return JsonResponse(exhibit_list, safe=False)
    return HttpResponseNotAllowed(['GET'])

def api_userStatus(request):
    if request.method == 'GET':
        status_lastActivityDate = [userActivity['last_activity_date'] for userActivity in UserActivity.objects.all().values()]
        status_isActivated = []
        for time in status_lastActivityDate:
            if datetime.datetime.now(datetime.timezone.utc) - time > datetime.timedelta(seconds = 30):
                status_isActivated.append({'currLoginStatus' : False})
            else:
                status_isActivated.append({'currLoginStatus' : True})
        status_list_full = [{**userActivity, **currLoginStatus} for userActivity, currLoginStatus in zip(UserActivity.objects.values(), status_isActivated)]
        status_list = []
        for status in status_list_full:
            tempUser = status['user_id']
            userTitle = UserWithTitle.objects.get(id=tempUser).title
            userName = UserWithTitle.objects.get(id=tempUser).username
            if status['dnd'] == True:
                status_list.append({'user_name' : userName, 'user_title' : userTitle, 'status' : 'dnd'})
            elif status['currLoginStatus'] == True:
                status_list.append({'user_name' : userName, 'user_title' : userTitle, 'status' : 'activated'})
            else:
                status_list.append({'user_name' : userName, 'user_title' : userTitle, 'status' : 'inactivated'})
        return JsonResponse(status_list, safe=False)
    return HttpResponseNotAllowed(['GET'])

@auth_func
def api_dndSwitch(request): #dndswitch 로 Boolean (True / False) 만 들어온다고 가정
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        dndswitch = request.POST.get('dndswitch')
        requestUser = request.user
        activity = UserActivity.objects.get(user = requestUser)
        activity.dnd = dndswitch
        activity.save()
        return HttpResponse(status=204)
    return HttpResponseNotAllowed(['POST'])

def api_blank(request):
    if request.method == 'GET':
        return HttpResponse(status=204)
    return HttpResponseNotAllowed(['GET'])

@auth_func
def api_getMyInfo(request):
    if request.method == 'GET':
        u = request.user.id
        userTitle = UserWithTitle.objects.get(id=u).title
        userName = UserWithTitle.objects.get(id=u).username
        info = [{'user_name' : userName, 'user_title' : userTitle}]
        return JsonResponse(info, safe=False)
    return HttpResponseNotAllowed(['GET'])

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

def api_signup(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = UserWithTitle.objects.create_user(username=username, password=password)
        except (ValueError, IntegrityError):
            return HttpResponseBadRequest()
        return HttpResponse(status=201)

@auth_func
def api_logout(request):
    if request.method == 'POST':
        logout(request)
        return HttpResponse(status=204)
    return HttpResponseNotAllowed(['POST'])

@ensure_csrf_cookie
def api_token(request):
    if request.method == 'GET':
        return HttpResponse(status=204)
    return HttpResponseNotAllowed(['GET'])
