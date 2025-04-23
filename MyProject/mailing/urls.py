from django.urls import path
from . import views

app_name = 'mailing'

urlpatterns = [
    # Recipient URLs
    path('recipients/', views.recipient_list, name='recipient_list'),  # Список получателей
    path('recipients/create/', views.recipient_create, name='recipient_create'),  # Создание получателя
    path('recipients/<int:pk>/update/', views.recipient_update, name='recipient_update'),  # Редактирование получателя
    path('recipients/<int:pk>/delete/', views.recipient_delete, name='recipient_delete'),  # Удаление получателя

    # Mailing URLs
    path('mailings/', views.mailing_list, name='mailing_list'),  # Список рассылок
    path('mailings/create/', views.mailing_create, name='mailing_create'),  # Создание рассылки
    path('mailings/<int:pk>/update/', views.mailing_update, name='mailing_update'),  # Редактирование рассылки
    path('mailings/<int:pk>/delete/', views.mailing_delete, name='mailing_delete'),  # Удаление рассылки
    path('mailings/<int:pk>/send/', views.send_mailing, name='send_mailing'),  # Отправка рассылки

    # Mailing Attempts URL
    path('mailings/<int:mailing_id>/attempts/', views.mailing_attempts, name='mailing_attempts'),  # Попытки рассылки
]