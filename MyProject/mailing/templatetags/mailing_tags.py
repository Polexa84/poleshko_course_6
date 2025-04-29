from django import template

register = template.Library()

@register.filter
def filter_status(queryset, status):
    """Фильтр для получения попыток по статусу."""
    return queryset.filter(status=status)

@register.filter
def get_recipient_email(recipient):
    """Получение email получателя с проверкой на None."""
    return recipient.email if recipient else "Не указан"