from django.contrib import admin
from .models import Recipient, Mailing

@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'last_attempt', 'owner')
    list_filter = ('status', 'last_attempt')

admin.site.register(Recipient)
