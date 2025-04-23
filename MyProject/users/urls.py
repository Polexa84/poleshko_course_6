from django.urls import path
from . import views

app_name = 'users'  # Добавляем app_name

urlpatterns = [
    path('register/', views.register, name='register'),
]