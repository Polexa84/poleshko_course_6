from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Создаем кастомный класс для админки
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_verified', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

# Регистрируем модель
admin.site.register(User, CustomUserAdmin)