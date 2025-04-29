from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q
from django.utils import timezone
from .forms import RecipientForm, MailingForm
from .models import Recipient, Mailing, MailingAttempt
from .tasks import send_mailing_task
from .services import process_mailing  # Импортируем улучшенную функцию
from users.utils import is_manager
import logging
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

logger = logging.getLogger(__name__)

@cache_page(60 * 15)  # Кешировать на 15 минут
@vary_on_cookie  # Разные кеши для разных пользователей
@login_required
def home(request):
    """Главная страница с приветствием и кнопкой перехода к статистике."""
    return render(request, 'home.html')


@login_required
def statistics(request):
    """Страница со статистикой рассылок."""
    mailings = Mailing.objects.all()

    stats = {
        'total_mailings': mailings.count(),
        'active_mailings': mailings.filter(
            status='running',
            start_time__lte=timezone.now(),
            end_time__gte=timezone.now()
        ).count(),
        'unique_recipients': Recipient.objects.distinct().count(),
    }

    attempts_stats = MailingAttempt.objects.filter(mailing__in=mailings).aggregate(
        total=Count('id'),
        success=Count('id', filter=Q(status='success')),
        failed=Count('id', filter=Q(status='failed')),
    )
    stats.update(attempts_stats)
    stats['success_rate'] = round((stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0, 2)

    return render(request, 'mailing/statistics.html', {'stats': stats, 'mailings': mailings})


@login_required
def mailing_attempts(request, pk):
    """Просмотр попыток отправки."""
    mailing = get_object_or_404(Mailing, pk=pk)

    if not is_manager(request.user) and mailing.owner != request.user:
        raise PermissionDenied

    attempts = mailing.attempts.select_related('recipient').order_by('-attempt_time')
    return render(request, 'mailing/mailing_attempts.html', {
        'mailing': mailing,
        'attempts': attempts,
    })

# Recipient CRUD
@login_required
def recipient_list(request):
    """Список получателей."""
    recipients = Recipient.objects.all() if is_manager(request.user) \
        else Recipient.objects.filter(owner=request.user)
    return render(request, 'mailing/recipient_list.html', {'recipients': recipients})


@login_required
def recipient_create(request):
    """Создание получателя."""
    if request.method == 'POST':
        form = RecipientForm(request.POST)
        if form.is_valid():
            recipient = form.save(commit=False)
            recipient.owner = request.user
            recipient.save()
            messages.success(request, 'Получатель успешно создан')
            return redirect('mailing:recipient_list')
    else:
        form = RecipientForm()
    return render(request, 'mailing/recipient_form.html', {'form': form})


@login_required
def recipient_update(request, pk):
    """Редактирование получателя."""
    recipient = get_object_or_404(Recipient, pk=pk)
    if recipient.owner != request.user and not is_manager(request.user):
        raise PermissionDenied

    if request.method == 'POST':
        form = RecipientForm(request.POST, instance=recipient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Получатель успешно обновлён')
            return redirect('mailing:recipient_list')
    else:
        form = RecipientForm(instance=recipient)
    return render(request, 'mailing/recipient_form.html', {'form': form, 'recipient': recipient})


@login_required
def recipient_delete(request, pk):
    """Удаление получателя."""
    recipient = get_object_or_404(Recipient, pk=pk)
    if recipient.owner != request.user and not is_manager(request.user):
        raise PermissionDenied

    if request.method == 'POST':
        recipient.delete()
        messages.success(request, 'Получатель успешно удалён')
        return redirect('mailing:recipient_list')
    return render(request, 'mailing/recipient_confirm_delete.html', {'recipient': recipient})


# Mailing CRUD
@login_required
def mailing_list(request):
    """Список рассылок."""
    mailings = Mailing.objects.all() if is_manager(request.user) \
        else Mailing.objects.filter(owner=request.user)
    return render(request, 'mailing/mailing_list.html', {
        'mailings': mailings.order_by('-created_at')
    })


@login_required
def mailing_create(request):
    """Создание рассылки."""
    if request.method == 'POST':
        form = MailingForm(request.POST, user=request.user)
        if form.is_valid():
            mailing = form.save(commit=False)
            mailing.owner = request.user
            mailing.save()
            form.save_m2m()
            messages.success(request, 'Рассылка успешно создана')
            return redirect('mailing:mailing_list')
    else:
        form = MailingForm(user=request.user)
    return render(request, 'mailing/mailing_form.html', {'form': form})


@login_required
def mailing_update(request, pk):
    """Редактирование рассылки."""
    mailing = get_object_or_404(Mailing, pk=pk)
    if mailing.owner != request.user and not is_manager(request.user):
        raise PermissionDenied

    if request.method == 'POST':
        form = MailingForm(request.POST, instance=mailing, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Рассылка успешно обновлена')
            return redirect('mailing:mailing_list')
    else:
        form = MailingForm(instance=mailing, user=request.user)
    return render(request, 'mailing/mailing_form.html', {'form': form})


@login_required
def mailing_delete(request, pk):
    """Удаление рассылки."""
    mailing = get_object_or_404(Mailing, pk=pk)
    if mailing.owner != request.user and not is_manager(request.user):
        raise PermissionDenied

    if request.method == 'POST':
        mailing.delete()
        messages.success(request, 'Рассылка успешно удалена')
        return redirect('mailing:mailing_list')
    return render(request, 'mailing/mailing_confirm_delete.html', {'mailing': mailing})


@require_http_methods(["POST"])
@login_required
def send_mailing(request, pk):
    """
    Унифицированный обработчик отправки рассылки с:
    - Проверкой прав
    - Поддержкой AJAX/синхронных запросов
    - Детальным логированием
    - Обработкой ошибок
    """
    mailing = get_object_or_404(Mailing, pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    # Проверка прав
    if not is_manager(request.user) and mailing.owner != request.user:
        logger.warning(f"Попытка несанкционированного доступа к рассылке {pk} пользователем {request.user}")
        if is_ajax:
            return JsonResponse({'error': 'Доступ запрещен'}, status=403)
        raise PermissionDenied

    # Проверка статуса
    if mailing.status != 'created':
        error_msg = f"Рассылка уже в статусе: {mailing.get_status_display()}"
        logger.warning(error_msg)
        if is_ajax:
            return JsonResponse({'error': error_msg}, status=400)
        messages.warning(request, error_msg)
        return redirect('mailing:mailing_list')

    try:
        if is_ajax:
            # Асинхронная обработка через Celery
            send_mailing_task.delay(mailing.pk)
            mailing.status = 'running'
            mailing.save(update_fields=['status'])

            logger.info(f"Запущена фоновая отправка рассылки {pk}")
            return JsonResponse(
                {'success': 'Рассылка поставлена в очередь на отправку'},
                status=202
            )
        else:
            # Синхронная обработка
            result = process_mailing(mailing)

            if result['status'] == 'success':
                msg = (f"Рассылка успешно отправлена. "
                       f"Успешно: {result['total_sent']}, "
                       f"Неудачно: {result['total_failed']}")
                messages.success(request, msg)
            else:
                messages.warning(request,
                                 f"Рассылка завершена с ошибками. Успешно: {result['total_sent']}")

            return redirect('mailing:mailing_attempts', pk=mailing.pk)

    except Exception as e:
        error_msg = f"Ошибка при отправке рассылки: {str(e)}"
        logger.error(error_msg, exc_info=True)

        if is_ajax:
            return JsonResponse({'error': error_msg}, status=500)

        messages.error(request, error_msg)
        return redirect('mailing:mailing_list')