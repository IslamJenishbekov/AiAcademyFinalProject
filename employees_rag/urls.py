from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_page, name='chat_page'),
    path('send_message/', views.send_message, name='send_message'),
]