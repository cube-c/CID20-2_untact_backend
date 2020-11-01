import json
import datetime
from json import JSONDecodeError
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import StatusType, UserWithTitle, Exhibit, Position

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
        status_list = []
        for user in UserWithTitle.objects.all():
            if user.is_superuser or user.id == request.user.id:
                continue
            if datetime.datetime.now(datetime.timezone.utc) - user.last_activity_date > datetime.timedelta(seconds = 20):
                user.status = StatusType.OFFLINE
                user.save()
            status_list.append({'name' : user.username, 'title' : user.title, 'status' : user.status})
        return JsonResponse(status_list, safe=False)
    return HttpResponseNotAllowed(['GET'])

@auth_func
def api_dndSwitch(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        dndswitch = request.POST.get('dndswitch')
        user_id = request.user.id
        user = UserWithTitle.objects.get(id = user_id)
        if dndswitch == "True":
            user.status = StatusType.DND
        else: # dndswitch == "False"
            user.status = StatusType.ONLINE
        user.save()
        return HttpResponse(status=204)
    return HttpResponseNotAllowed(['POST'])

def api_blank(request):
    if request.method == 'GET':
        return HttpResponse(status=204)
    return HttpResponseNotAllowed(['GET'])

def api_getMyInfo(request):
    if request.method == 'GET':
        u = request.user.id
        userTitle = UserWithTitle.objects.get(id=u).title
        userName = UserWithTitle.objects.get(id=u).username
        info = {'user_name' : userName, 'user_title' : userTitle}
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
        user_id = request.user.id
        userLogout = UserWithTitle.objects.get(id = user_id)
        userLogout.status = StatusType.OFFLINE
        userLogout.save()
        logout(request)
        return HttpResponse(status=204)
    return HttpResponseNotAllowed(['POST'])

@ensure_csrf_cookie
def api_token(request):
    if request.method == 'GET':
        return HttpResponse(status=204)
    return HttpResponseNotAllowed(['GET'])
