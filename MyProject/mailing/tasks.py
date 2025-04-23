from celery import shared_task
from .models import Mailing, MailingAttempt
from postal_service.models import Message  # Импортируйте модель Message
from django.core.mail import send_mail  # Импортируйте send_mail
from django.utils import timezone

@shared_task
def send_mailing_task(mailing_pk):
    """Celery-таска для отправки рассылки."""
    mailing = Mailing.objects.get(pk=mailing_pk)

    # Получаем список получателей для этой рассылки
    recipients = mailing.recipients.all()

    # Получаем сообщение для этой рассылки
    message = mailing.message  # Получаем объект Message

    for recipient in recipients:
        try:
            send_mail(
                message.subject,  # Тема сообщения
                message.body,  # Текст сообщения
                'from@example.com',  # Отправитель (укажите свой адрес)
                [recipient.email],  # Получатель (список email-адресов)
                fail_silently=False,  # Если True, ошибки будут игнорироваться
            )
            # Если успешно:
            MailingAttempt.objects.create(
                mailing=mailing,
                status='success',
                server_response='200 OK',
                timestamp=timezone.now()  # Добавляем временную метку
            )
        except Exception as e:
            # Если ошибка:
            MailingAttempt.objects.create(
                mailing=mailing,
                status='failed',
                server_response=str(e),
                timestamp=timezone.now()  # Добавляем временную метку
            )

    # Обновляем статус рассылки на "completed"
    mailing.status = 'completed'
    mailing.save()