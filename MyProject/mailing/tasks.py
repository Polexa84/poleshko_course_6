from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from .models import Mailing, MailingAttempt
from postal_service.models import Message
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, retry_backoff=True, max_retries=3)
def send_mailing_task(self, mailing_pk):
    """
    Улучшенная Celery-таска для отправки рассылки с:
    - Подробным логированием
    - Гибкой обработкой ошибок
    - Корректным обновлением статусов
    """
    try:
        mailing = Mailing.objects.select_related('message').get(pk=mailing_pk)

        # Проверяем, что рассылка должна быть запущена
        if mailing.status == 'completed':
            logger.warning(f"Рассылка {mailing_pk} уже завершена, пропускаем")
            return

        # Обновляем статус на "running" перед началом отправки
        mailing.status = 'running'
        mailing.save(update_fields=['status'])

        recipients = mailing.recipients.all()
        message = mailing.message
        total_sent = 0
        total_failed = 0

        for recipient in recipients:
            try:
                send_mail(
                    subject=message.subject,
                    message=message.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )

                MailingAttempt.objects.create(
                    mailing=mailing,
                    recipient=recipient,
                    status='success',
                    server_response='200 OK',
                    attempt_time=timezone.now()
                )
                total_sent += 1

            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                logger.error(f"Ошибка отправки для {recipient.email}: {error_msg}")

                MailingAttempt.objects.create(
                    mailing=mailing,
                    recipient=recipient,
                    status='failed',
                    server_response=error_msg,
                    attempt_time=timezone.now()
                )
                total_failed += 1

        # Финализируем статус рассылки
        if total_failed == 0:
            mailing.status = 'completed'
        else:
            mailing.status = 'partially_completed'  # Можно добавить этот статус в модель

        mailing.save(update_fields=['status'])

        logger.info(
            f"Рассылка {mailing_pk} завершена. "
            f"Успешно: {total_sent}, Неудачно: {total_failed}"
        )

        return {
            'total_sent': total_sent,
            'total_failed': total_failed,
            'mailing_id': mailing_pk
        }

    except Mailing.DoesNotExist:
        logger.error(f"Рассылка {mailing_pk} не найдена")
        raise
    except Exception as e:
        logger.critical(f"Критическая ошибка в задаче: {str(e)}")
        mailing.status = 'failed'
        mailing.save(update_fields=['status'])
        raise self.retry(exc=e, countdown=60)