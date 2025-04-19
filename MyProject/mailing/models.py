from django.db import models
from postal_service.models import Message  # Импортируем модель Message из postal_service

class Recipient(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email")
    full_name = models.CharField(max_length=255, verbose_name="Ф.И.О.")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"

class Mailing(models.Model):
    start_time = models.DateTimeField(verbose_name='Дата и время первой отправки')
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
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name='Сообщение')  # Указываем на модель Message из postal_service
    recipients = models.ManyToManyField(Recipient, verbose_name='Получатели')

    def __str__(self):
        return f"Рассылка {self.pk}: {self.message.subject}"

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'