import json
from json import JSONDecodeError
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Exhibit
from .models import Position

def auth_func(func):
    def wrapper_function(*args, **kwargs):
        if (args[0].user.is_authenticated):
            return func(*args, **kwargs)
        return HttpResponse(status=401)
    return wrapper_function

def api_exhibit(request):
    if request.method == 'GET':
        exhibit_position_id_list = [exhibit['position_id'] for exhibit in Exhibit.objects.all().values()]
        exhibit_position_list = [list(Position.objects.filter(position_id=position_id).values())[0] for position_id in exhibit_position_id_list]
        exhibit_all_list = [{**exhibit, **position} for exhibit, position in zip(Exhibit.objects.all().values(), exhibit_position_list)]
        return JsonResponse(exhibit_all_list, safe=False)
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
