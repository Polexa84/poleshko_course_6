from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailing.models import Mailing, Recipient
from users.models import User


class Command(BaseCommand):
    help = 'Создает группу "Менеджеры" и назначает все необходимые права'

    def handle(self, *args, **options):
        manager_group, created = Group.objects.get_or_create(name='Менеджеры')

        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Менеджеры" создана'))
        else:
            self.stdout.write(self.style.WARNING('Группа "Менеджеры" уже существует, обновляем права'))

        # Собираем все необходимые права
        permissions = []

        # Автоматически созданное permission для view_user
        view_user_perm = Permission.objects.get(
            content_type=ContentType.objects.get_for_model(User),
            codename='view_user'
        )
        permissions.append(view_user_perm)

        # Кастомное permission для block_user
        block_user_perm = Permission.objects.get(
            content_type=ContentType.objects.get_for_model(User),
            codename='block_user'
        )
        permissions.append(block_user_perm)

        # Права для модели Recipient
        recipient_permissions = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(Recipient),
            codename__in=['view_all_recipients', 'block_recipient']
        )
        permissions.extend(recipient_permissions)

        # Права для модели Mailing
        mailing_permissions = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(Mailing),
            codename__in=['view_all_mailings', 'disable_mailing']
        )
        permissions.extend(mailing_permissions)

        # Назначаем права группе
        manager_group.permissions.set(permissions)

        self.stdout.write(self.style.SUCCESS(
            'Успешно назначены следующие права для группы "Менеджеры":\n'
            '- Просмотр пользователей (встроенное право)\n'
            '- Блокировка пользователей\n'
            '- Просмотр и блокировка получателей\n'
            '- Просмотр всех рассылок и их отключение'
        ))