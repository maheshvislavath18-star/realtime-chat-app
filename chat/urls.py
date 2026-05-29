from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_home, name='chat_home'),

    # 👇 PRIVATE CHAT ROUTE (NEW)
    path('chat/<str:user2>/', views.private_chat, name='private_chat'),
]