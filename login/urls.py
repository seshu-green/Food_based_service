from django.urls import path
from login.views import *
from django.conf.urls import include

urlpatterns = [
    path('',enter),
    path('user/',include('user.urls')),
]