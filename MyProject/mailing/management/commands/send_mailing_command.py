from django.core.management.base import BaseCommand, CommandError
from mailing.models import Mailing
from mailing.tasks import send_mailing_task  # Импортируем celery-таску

class Command(BaseCommand):
    help = 'Отправляет рассылку по ID'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', nargs='+', type=int)

    def handle(self, *args, **options):
        for mailing_id in options['mailing_id']:
            try:
                mailing = Mailing.objects.get(pk=mailing_id)
            except Mailing.DoesNotExist:
                raise CommandError('Рассылка с ID "%s" не найдена' % mailing_id)

            if mailing.status != 'completed':
                # Запускаем celery-таску для отправки рассылки
                send_mailing_task.delay(mailing.pk)

                self.stdout.write(self.style.SUCCESS(f'Рассылка "{mailing.pk}" поставлена в очередь на отправку'))
            else:
                self.stdout.write(self.style.WARNING(f'Рассылка "{mailing.pk}" уже отправлена'))