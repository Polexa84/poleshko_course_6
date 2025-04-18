from django.urls import path
from .views import recipient_list, recipient_create, recipient_update, recipient_delete

urlpatterns = [
    path('', recipient_list, name='recipient_list'),
    path('create/', recipient_create, name='recipient_create'),
    path('update/<int:pk>/', recipient_update, name='recipient_update'),
    path('delete/<int:pk>/', recipient_delete, name='recipient_delete'),
]