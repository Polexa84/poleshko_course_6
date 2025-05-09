from django.core.management.base import BaseCommand
from django.utils import timezone
from mailing.models import Mailing
from mailing.services import process_mailing


class Command(BaseCommand):
    help = 'Send scheduled mailings'

    def handle(self, *args, **options):
        now = timezone.now()
        mailings = Mailing.objects.filter(
            status='created',
            start_time__lte=now,
            end_time__gte=now
        )

        for mailing in mailings:
            self.stdout.write(f"Processing mailing #{mailing.id}")
            process_mailing(mailing)

        self.stdout.write(self.style.SUCCESS(f"Processed {mailings.count()} mailings"))