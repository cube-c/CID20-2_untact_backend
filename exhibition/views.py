import json
from json import JSONDecodeError
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Exhibit, Position, UserWithTitle

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
