from django.contrib.auth.models import Group

def is_manager(user):
    """Проверяет, является ли пользователь менеджером."""
    return user.groups.filter(name='Менеджеры').exists()