from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('recipients/', include('mailing.urls')),
    path('postal_service/', include('postal_service.urls')),
    path('', views.home, name='home'),  # URL для главной страницы
]