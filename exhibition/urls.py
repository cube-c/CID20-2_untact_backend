from django.urls import path

from . import views

urlpatterns = [
    path('token/', views.api_token),
    path('login/', views.api_login),
    path('logout/', views.api_logout),
    path('signup/', views.api_signup),
    path('exhibit/', views.api_exhibit),
    path('userStatus/', views.api_userStatus),
    path('dndSwitch/', views.api_dndSwitch),
    path('myInfo/', views.api_getMyInfo),
    path('blank/', views.api_blank)
]