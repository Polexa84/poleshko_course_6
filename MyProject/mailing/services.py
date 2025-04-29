from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from .models import MailingAttempt
import logging

logger = logging.getLogger(__name__)


def send_single_mail(mailing, recipient):
    """Отправляет одно письмо и создает запись о попытке"""
    try:
        # Отправка письма
        send_mail(
            subject=mailing.message.subject,
            message=mailing.message.body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient.email],
            fail_silently=False
        )
        status = 'success'
        response = '200 OK'
    except Exception as e:
        status = 'failed'
        response = f"{type(e).__name__}: {str(e)}"
        logger.error(f"Ошибка отправки для {recipient.email}: {response}")

    # Создание записи о попытке
    attempt = MailingAttempt.objects.create(
        mailing=mailing,
        recipient=recipient,
        status=status,
        server_response=response,
        attempt_time=timezone.now()
    )

    return status == 'success'


def process_mailing(mailing):
    """Основная функция обработки рассылки с улучшениями"""
    try:
        # Начало обработки - обновляем статус
        mailing.status = 'running'
        mailing.last_attempt = timezone.now()
        mailing.save(update_fields=['status', 'last_attempt'])

        total_sent = 0
        total_failed = 0

        # Оптимизированный запрос для получателей
        recipients = mailing.recipients.all().only('email', 'full_name')

        for recipient in recipients:
            if send_single_mail(mailing, recipient):
                total_sent += 1
            else:
                total_failed += 1

        # Определяем финальный статус
        if total_failed == 0:
            mailing.status = 'completed'
        elif total_sent > 0:
            mailing.status = 'partially_completed'
        else:
            mailing.status = 'failed'

        mailing.last_attempt = timezone.now()
        mailing.save(update_fields=['status', 'last_attempt'])

        logger.info(
            f"Рассылка {mailing.pk} завершена. "
            f"Успешно: {total_sent}, Неудачно: {total_failed}"
        )

        return {
            'status': 'success',
            'total_sent': total_sent,
            'total_failed': total_failed
        }

    except Exception as e:
        logger.error(f"Критическая ошибка при обработке рассылки {mailing.pk}: {str(e)}")
        mailing.status = 'failed'
        mailing.last_attempt = timezone.now()
        mailing.save(update_fields=['status', 'last_attempt'])
        raise