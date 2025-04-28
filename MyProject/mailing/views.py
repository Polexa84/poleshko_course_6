from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q, Sum
from django.utils import timezone
from .forms import RecipientForm, MailingForm
from .models import Recipient, Mailing, MailingAttempt
from .tasks import send_mailing_task
from users.utils import is_manager


@login_required
def home(request):
    """Главная страница со статистикой."""
    mailings = Mailing.objects.all()

    # Основная статистика
    stats = {
        'total_mailings': mailings.count(),
        'active_mailings': mailings.filter(
            status='running',
            start_time__lte=timezone.now(),
            end_time__gte=timezone.now()
        ).count(),
        'unique_recipients': Recipient.objects.distinct().count(),
    }

    # Статистика по попыткам
    attempts_stats = MailingAttempt.objects.filter(mailing__in=mailings).aggregate(
        total=Count('id'),
        success=Count('id', filter=Q(status='success')),
        failed=Count('id', filter=Q(status='failed')),
    )
    stats.update(attempts_stats)

    # Рассчёт процента успешных
    stats['success_rate'] = round(
        (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0,
        2
    )

    return render(request, 'home.html', {'stats': stats})


@login_required
def mailing_attempts(request, pk):
    """Просмотр попыток отправки."""
    mailing = get_object_or_404(Mailing, pk=pk)

    if not is_manager(request.user) and mailing.owner != request.user:
        raise PermissionDenied

    attempts = mailing.attempts.all().order_by('-attempt_time')
    return render(request, 'mailing/mailing_attempts.html', {
        'mailing': mailing,
        'attempts': attempts,
    })


# Recipient CRUD
@login_required
def recipient_list(request):
    """Список получателей с проверкой прав."""
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
    """Редактирует существующего получателя."""
    recipient = get_object_or_404(Recipient, pk=pk)

    if is_manager(request.user):
        messages.error(request, 'Менеджеры не могут редактировать получателей')
        return redirect('mailing:recipient_list')

    if recipient.owner != request.user:
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
    """Удаляет получателя."""
    recipient = get_object_or_404(Recipient, pk=pk)

    if is_manager(request.user):
        messages.error(request, 'Менеджеры не могут удалять получателей')
        return redirect('mailing:recipient_list')  # Или другой подходящий редирект

    if recipient.owner != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        recipient.delete()
        messages.success(request, 'Получатель успешно удалён')
        return redirect('mailing:recipient_list')
    return render(request, 'mailing/recipient_confirm_delete.html', {'recipient': recipient})


# Mailing CRUD
@login_required
def mailing_list(request):
    """Список рассылок с проверкой прав."""
    if is_manager(request.user):
        mailings = Mailing.objects.all().order_by('-created_at')
    else:
        mailings = Mailing.objects.filter(owner=request.user).order_by('-created_at')

    return render(request, 'mailing/mailing_list.html', {'mailings': mailings})


@login_required
def mailing_create(request):
    """Создание новой рассылки."""
    if request.method == 'POST':
        form = MailingForm(request.POST, user=request.user)
        if form.is_valid():
            mailing = form.save(commit=False)
            mailing.owner = request.user
            mailing.save()
            form.save_m2m()  # Для ManyToMany полей
            messages.success(request, 'Рассылка успешно создана')
            return redirect('mailing:mailing_list')
    else:
        form = MailingForm(user=request.user)
    return render(request, 'mailing/mailing_form.html', {'form': form})


@login_required
def mailing_update(request, pk):
    """Редактирование рассылки."""
    mailing = get_object_or_404(Mailing, pk=pk)

    if not is_manager(request.user) and mailing.owner != request.user:
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
    """Удаляет рассылку."""
    mailing = get_object_or_404(Mailing, pk=pk)

    if is_manager(request.user):
        messages.error(request, 'Менеджеры не могут удалять рассылки')
        return redirect('mailing:mailing_list')  # Или другой подходящий редирект

    if mailing.owner != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        mailing.delete()
        messages.success(request, 'Рассылка успешно удалена')
        return redirect('mailing:mailing_list')
    return render(request, 'mailing/mailing_confirm_delete.html', {'mailing': mailing})


@login_required
@csrf_exempt
def send_mailing(request, pk):
    """API для запуска рассылки через Celery."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    mailing = get_object_or_404(Mailing, pk=pk)

    # Проверка прав
    if not is_manager(request.user) and mailing.owner != request.user:
        return JsonResponse(
            {'error': 'Permission denied'},
            status=403
        )

    # Проверка статуса
    if mailing.status in ['running', 'completed']:
        return JsonResponse(
            {'error': f'Mailing already {mailing.get_status_display()}'},
            status=400
        )

    # Запуск задачи
    try:
        send_mailing_task.delay(mailing.pk)
        mailing.status = 'running'
        mailing.save(update_fields=['status'])
        return JsonResponse(
            {'success': f'Mailing {pk} started'},
            status=202
        )
    except Exception as e:
        return JsonResponse(
            {'error': str(e)},
            status=500
        )