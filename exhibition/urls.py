from django.urls import path

from . import views

urlpatterns = [
    path('token/', views.api_token),
    path('login/', views.api_login),
    path('signup/', views.api_signup),
    path('exhibit/', views.api_exhibit),
    # path('position/<position_id>/', views.api_position)
]