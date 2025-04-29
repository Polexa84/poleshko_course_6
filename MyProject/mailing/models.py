from django.db import models
from postal_service.models import Message
from django.contrib.auth.models import User  # Импортируем User


class Recipient(models.Model):
    """Модель получателя рассылки."""
    email = models.EmailField(unique=True, verbose_name="Email")
    full_name = models.CharField(max_length=255, verbose_name="Ф.И.О.")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец")  # Добавляем поле owner

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"


class Mailing(models.Model):
    """Модель рассылки с настройками отправки."""
    start_time = models.DateTimeField(verbose_name='Дата и время первой отправки')
    last_attempt = models.DateTimeField(null=True, blank=True, verbose_name='Последняя попытка')
    end_time = models.DateTimeField(verbose_name='Дата и время окончания отправки')
    status = models.CharField(
        max_length=20,
        choices=[
            ('completed', 'Завершена'),
            ('created', 'Создана'),
            ('running', 'Запущена'),
        ],
        default='created',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name='Сообщение')
    recipients = models.ManyToManyField(Recipient, verbose_name='Получатели')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец")  # Добавляем поле owner

    def __str__(self):
        return f"Рассылка #{self.pk}"

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class MailingAttempt(models.Model):
    """Модель для хранения результатов попытки отправки рассылки."""
    ATTEMPT_STATUS = [
        ('success', 'Успешно'),
        ('failed', 'Не успешно'),
    ]

    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        verbose_name='Рассылка',
        related_name='attempts'
    )
    recipient = models.ForeignKey(  # Добавляем связь с получателем
        Recipient,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Получатель'
    )
    attempt_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время попытки'
    )
    status = models.CharField(
        max_length=10,
        choices=ATTEMPT_STATUS,
        verbose_name='Статус'
    )
    server_response = models.TextField(
        blank=True,
        null=True,
        verbose_name='Ответ сервера'
    )

    def __str__(self):
        return f"Попытка #{self.pk} ({self.status})"

    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылок'
        ordering = ['-attempt_time']