from django.urls import path
from . import views

app_name = 'mailing'

urlpatterns = [
    # Главная и статистика
    path('', views.home, name='home'),
    path('statistics/', views.statistics, name='statistics'),

    # Recipient URLs
    path('recipients/', views.recipient_list, name='recipient_list'),
    path('recipients/create/', views.recipient_create, name='recipient_create'),
    path('recipients/<int:pk>/update/', views.recipient_update, name='recipient_update'),
    path('recipients/<int:pk>/delete/', views.recipient_delete, name='recipient_delete'),

    # Mailing URLs
    path('mailings/', views.mailing_list, name='mailing_list'),
    path('mailings/create/', views.mailing_create, name='mailing_create'),
    path('mailings/<int:pk>/update/', views.mailing_update, name='mailing_update'),
    path('mailings/<int:pk>/delete/', views.mailing_delete, name='mailing_delete'),
    path('mailings/<int:pk>/send/', views.send_mailing, name='send_mailing'),

    # Mailing Attempts URL
    path('mailings/<int:pk>/attempts/', views.mailing_attempts, name='mailing_attempts'),
]