from django.urls import path

from . import views

urlpatterns = [
    path('token/', views.api_token),
    path('login/', views.api_login),
    path('exhibit/', views.api_exhibit),
    path('userStatus/', views.api_userStatus),
    # path('position/<position_id>/', views.api_position)
]