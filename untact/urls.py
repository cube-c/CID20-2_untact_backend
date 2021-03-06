"""untact URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls import url
from django.views.static import serve
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

def protected_serve(request, path, document_root=None):
    if request.user.is_authenticated:
        return serve(request, path, document_root)
    return HttpResponse(status=401)

urlpatterns = [
    path('message/', include('message.urls')),
    path('api/', include('exhibition.urls')),
    path('admin/', admin.site.urls),
    url(r'^media/(?P<path>.*)$', protected_serve, {
    'document_root': settings.MEDIA_ROOT}),
]