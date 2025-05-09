from django.urls import path
from . import views

app_name = 'postal_service'
"""URL-адреса для приложения postal_service."""

urlpatterns = [
    path('', views.message_list, name='message_list'),
    path('create/', views.message_create, name='message_create'),
    path('<int:pk>/update/', views.message_update, name='message_update'),
    path('<int:pk>/delete/', views.message_delete, name='message_delete'),
]