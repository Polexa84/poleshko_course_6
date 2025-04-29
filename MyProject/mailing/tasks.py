from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from .models import Mailing, MailingAttempt
import logging
from django.db import transaction

logger = logging.getLogger(__name__)


@shared_task(bind=True, retry_backoff=True, max_retries=3, autoretry_for=(Exception,))
def send_mailing_task(self, mailing_pk):
    """
    Улучшенная Celery-таска для отправки рассылки с:
    - Атомарными операциями
    - Детальным логированием
    - Оптимизированными запросами к БД
    - Поддержкой частичной отправки
    """
    try:
        with transaction.atomic():
            # Блокируем запись для предотвращения race condition
            mailing = Mailing.objects.select_related('message') \
                .select_for_update() \
                .get(pk=mailing_pk)

            # Проверяем статус рассылки
            if mailing.status not in ['created', 'partially_completed']:
                logger.warning(f"Рассылка {mailing_pk} в статусе {mailing.status}, пропускаем")
                return

            # Обновляем статус
            mailing.status = 'running'
            mailing.last_attempt = timezone.now()
            mailing.save(update_fields=['status', 'last_attempt'])

        # Получаем получателей вне транзакции
        recipients = mailing.recipients.all().only('email', 'full_name')
        message = mailing.message
        total_sent = 0
        total_failed = 0

        for recipient in recipients:
            try:
                # Отправка письма
                send_mail(
                    subject=message.subject,
                    message=message.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )

                # Логируем успешную попытку
                with transaction.atomic():
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
                logger.error(f"Ошибка для {recipient.email}: {error_msg}")

                # Логируем неудачную попытку
                with transaction.atomic():
                    MailingAttempt.objects.create(
                        mailing=mailing,
                        recipient=recipient,
                        status='failed',
                        server_response=error_msg,
                        attempt_time=timezone.now()
                    )
                total_failed += 1

        # Финализируем статус
        with transaction.atomic():
            mailing.refresh_from_db()
            if total_failed == 0:
                mailing.status = 'completed'
            elif total_sent > 0:
                mailing.status = 'partially_completed'
            else:
                mailing.status = 'failed'

            mailing.last_attempt = timezone.now()
            mailing.save(update_fields=['status', 'last_attempt'])

        logger.info(
            f"Рассылка {mailing_pk} завершена. "
            f"Успешно: {total_sent}, Неудачно: {total_failed}"
        )

        return {
            'status': 'completed',
            'mailing_id': mailing_pk,
            'success_count': total_sent,
            'failed_count': total_failed,
            'timestamp': timezone.now().isoformat()
        }

    except Mailing.DoesNotExist:
        logger.error(f"Рассылка {mailing_pk} не найдена")
        raise
    except Exception as e:
        logger.critical(f"Критическая ошибка: {str(e)}", exc_info=True)
        try:
            with transaction.atomic():
                mailing = Mailing.objects.get(pk=mailing_pk)
                mailing.status = 'failed'
                mailing.last_attempt = timezone.now()
                mailing.save(update_fields=['status', 'last_attempt'])
        except Exception:
            logger.error("Не удалось обновить статус рассылки после ошибки")

        raise self.retry(exc=e, countdown=60)