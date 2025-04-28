from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import RecipientForm, MailingForm
from .tasks import send_mailing_task
from .models import Recipient, Mailing, MailingAttempt
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from users.utils import is_manager
from django.db.models import Count, Q, Sum
from django.utils import timezone


@login_required
def home(request):
    """Главная страница со статистикой (без фильтрации по дате)."""
    mailings = Mailing.objects.all()  # Получаем все рассылки

    # Основная статистика
    total_mailings = mailings.count()
    active_mailings = mailings.filter(
        status='running',
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now()
    ).count()
    # Уникальных получателей считаем по всем рассылкам, чтобы не зависеть от фильтра
    unique_recipients = Recipient.objects.distinct().count()

    # Статистика по попыткам
    attempts_stats = MailingAttempt.objects.filter(mailing__in=mailings).aggregate(
        total=Count('id'),
        success=Count('id', filter=Q(status='success')),
        failed=Count('id', filter=Q(status='failed')),
        total_messages=Sum('messages_sent')  # Суммируем отправленные сообщения
    )

    # Рассчет процента успешных
    success_rate = 0
    if attempts_stats['total'] > 0:
        success_rate = (attempts_stats['success'] / attempts_stats['total']) * 100

    # Статистика по последним рассылкам
    recent_mailings = Mailing.objects.order_by('-created_at')[:5]

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_recipients': unique_recipients,
        'total_attempts': attempts_stats['total'],
        'successful_attempts': attempts_stats['success'],
        'failed_attempts': attempts_stats['failed'],
        'success_rate': round(success_rate, 2),
        'total_messages': attempts_stats['total_messages'] or 0,
        'recent_mailings': recent_mailings,
    }

    return render(request, 'home.html', context)


@login_required
def mailing_attempts(request, mailing_id):
    """Просмотр попыток отправки для конкретной рассылки."""
    mailing = get_object_or_404(Mailing, pk=mailing_id)
    attempts = mailing.attempts.all().order_by('-attempt_time')  # Получаем все попытки и сортируем

    return render(request, 'mailing/mailing_attempts.html', {
        'mailing': mailing,
        'attempts': attempts,
    })


# Recipient CRUD Views
@login_required
def recipient_list(request):
    """Отображает список получателей с учетом владельца и роли."""
    if is_manager(request.user):
        recipients = Recipient.objects.all().order_by('full_name')  # Менеджеры видят всех
    else:
        recipients = Recipient.objects.filter(owner=request.user).order_by('full_name')  # Пользователи - только свои
    return render(request, 'mailing/recipient_list.html', {'recipients': recipients})


@login_required
def recipient_create(request):
    """Создает нового получателя."""
    if request.method == 'POST':
        form = RecipientForm(request.POST)
        if form.is_valid():
            recipient = form.save(commit=False)
            recipient.owner = request.user  # Устанавливаем владельца
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
        return redirect('mailing:recipient_list')  # Или другой подходящий редирект

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


# Mailing CRUD Views
@login_required
def mailing_list(request):
    """Отображает список рассылок с учетом владельца и роли."""
    if is_manager(request.user):
        mailings = Mailing.objects.all().order_by('-created_at')  # Менеджеры видят все рассылки
    else:
        mailings = Mailing.objects.filter(owner=request.user).order_by('-created_at')  # Пользователи видят только свои
    return render(request, 'mailing/mailing_list.html', {'mailings': mailings})


@login_required
def mailing_create(request):
    """Создает новую рассылку."""
    if request.method == 'POST':
        form = MailingForm(request.POST)
        if form.is_valid():
            mailing = form.save(commit=False)  # Не сохраняем сразу, чтобы добавить owner
            mailing.owner = request.user  # Устанавливаем владельца
            mailing.save()  # Теперь сохраняем
            messages.success(request, 'Рассылка успешно создана')
            return redirect('mailing:mailing_list')
    else:
        form = MailingForm()
    return render(request, 'mailing/mailing_form.html', {'form': form})


@login_required
def mailing_update(request, pk):
    """Редактирует существующую рассылку."""
    mailing = get_object_or_404(Mailing, pk=pk)

    if is_manager(request.user):
        messages.error(request, 'Менеджеры не могут редактировать рассылки')
        return redirect('mailing:mailing_list')  # Или другой подходящий редирект

    if mailing.owner != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = MailingForm(request.POST, instance=mailing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Рассылка успешно обновлена')
            return redirect('mailing:mailing_list')
    else:
        form = MailingForm(instance=mailing)
    return render(request, 'mailing/mailing_form.html', {'form': form, 'mailing': mailing})


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
def send_mailing(request, pk):
    """Запускает рассылку с проверкой статуса."""
    mailing = get_object_or_404(Mailing, pk=pk)

    if is_manager(request.user):
        messages.error(request, 'Менеджеры не могут запускать рассылки')
        return redirect('mailing:mailing_list')  # Или другой подходящий редирект

    if mailing.owner != request.user:
        raise PermissionDenied

    if mailing.status == 'completed':
        messages.warning(request, 'Эта рассылка уже была отправлена')
        return redirect('mailing:mailing_list')

    if mailing.status == 'running':
        messages.warning(request, 'Эта рассылка уже выполняется')
        return redirect('mailing:mailing_list')

    # Запускаем асинхронную задачу
    send_mailing_task.delay(mailing.pk)
    mailing.status = 'running'
    mailing.save()

    messages.success(request, 'Рассылка успешно запущена')
    return redirect('mailing:mailing_list')