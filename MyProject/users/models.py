from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        verbose_name=_('Email'),
        error_messages={
            'unique': _('Пользователь с таким email уже существует.'),
        }
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Подтверждён')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Телефон')
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name=_('Аватар')
    )

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('Группы'),
        blank=True,
        help_text=_('Группы, к которым принадлежит пользователь.'),
        related_name="custom_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('Права пользователя'),
        blank=True,
        help_text=_('Конкретные права для этого пользователя.'),
        related_name="custom_user_set",
        related_query_name="user",
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')