# services.py
from django.core.mail import send_mail
from django.conf import settings
from .models import MailingAttempt, Mailing
from django.core.exceptions import PermissionDenied


def send_mailing(mailing_pk, user_pk=None):
    """
    Отправляет рассылку и логирует попытки.
    """
    mailing = Mailing.objects.get(pk=mailing_pk)

    # Проверка прав (если user_pk передан)
    if user_pk and mailing.owner_id != user_pk:
        raise PermissionDenied("У вас нет прав на отправку этой рассылки.")

    subject = mailing.message.subject
    message_body = mailing.message.body
    recipients = mailing.recipients.all()

    for recipient in recipients:
        try:
            send_mail(
                subject,
                message_body,
                settings.DEFAULT_FROM_EMAIL,
                [recipient.email],
                fail_silently=False,
            )
            # Логируем успех
            MailingAttempt.objects.create(
                mailing=mailing,
                status='success',
                server_response='OK',
                messages_sent=1,  # Учитываем количество отправленных
            )
        except Exception as e:
            # Логируем ошибку
            MailingAttempt.objects.create(
                mailing=mailing,
                status='failed',
                server_response=str(e),
                messages_sent=0,
            )

    # Обновляем статус рассылки после отправки
    mailing.status = 'completed'
    mailing.save()