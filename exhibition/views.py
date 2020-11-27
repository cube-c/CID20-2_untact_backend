import json
import datetime
from json import JSONDecodeError
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import transaction
from .models import UserWithTitle, Exhibit, Position
from message.models import Invitation

def auth_func(func):
    def wrapper_function(*args, **kwargs):
        if (args[0].user.is_authenticated):
            return func(*args, **kwargs)
        return HttpResponse(status=401)
    return wrapper_function

@auth_func
def api_exhibit(request):
    if request.method == 'GET':
        exhibit_query = Exhibit.objects.filter(position_id__isnull=False).select_related('position')
        exhibit_list = [exhibit.data() for exhibit in exhibit_query]
        return JsonResponse(exhibit_list, safe=False)
    return HttpResponseNotAllowed(['GET'])

@auth_func
def api_userStatus(request):
    if request.method == 'GET':
        status_list = []
        for user in UserWithTitle.objects.all():
            #if user.is_superuser or user.id == request.user.id:
            #    continue
            status = ''
            if user.is_online:
                if user.is_dnd:
                    status = 'dnd'
                else:
                    status = 'online'
            else:
                status = 'offline'
            status_list.append({'name' : user.username, 'title' : user.title, 'status' : status})
        return JsonResponse(status_list, safe=False)
    return HttpResponseNotAllowed(['GET'])

@auth_func
def api_dndSwitch(request):
    if request.method == 'POST':
        dndswitch = request.POST.get('dndswitch')
        user_id = request.user.id
        user = UserWithTitle.objects.get(id = user_id)
        user.is_dnd = (dndswitch == "True")
        user.save()
        return HttpResponse(status=204)
    return HttpResponseNotAllowed(['POST'])

@auth_func
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
            if len(username) < 4 or len(username) > 16 or len(password) < 8 or len(password) > 128 or not username.isalnum():
                raise ValueError
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
