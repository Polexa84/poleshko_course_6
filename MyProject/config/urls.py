from . import views
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from users import views as user_views #Импортируем user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('mailing/', include('mailing.urls')),
    path('postal_service/', include('postal_service.urls')),
    path('users/', include('users.urls', namespace='users')),
    path('login/', user_views.login_view, name='login'), #Используем user_views
    path('logout/', user_views.logout_view, name='logout'),#Используем user_views
    path('', views.home, name='home'),  # URL для главной страницы
]