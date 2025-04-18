# mailing/urls.py
from django.urls import path
from . import views

app_name = 'mailing'

urlpatterns = [
    path('', views.recipient_list, name='recipient_list'),
    path('create/', views.recipient_create, name='recipient_create'),
    path('<int:pk>/update/', views.recipient_update, name='recipient_update'),
    path('<int:pk>/delete/', views.recipient_delete, name='recipient_delete'),
]