from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    """Модель сообщения."""
    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Тело письма")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец")

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"