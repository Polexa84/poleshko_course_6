from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('recipients/', include('mailing.urls')),  # Подключаем URLs из приложения mailing
]