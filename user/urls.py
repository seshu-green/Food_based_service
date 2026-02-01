from django.urls import path
from user.views import log, home, out, flush, save_chat_history, start_chat

urlpatterns = [
    path('log/', log, name='log'),
    path('home/', home, name='home'),
    path('flush/', flush, name='flush'),
    path('out/', out, name='bye'),
    path('save_chat_history/', save_chat_history, name='save_chat_history'),
    path('start_chat/', start_chat, name='start_chat'),  # <-- add this
]
