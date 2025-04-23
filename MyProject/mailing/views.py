from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Recipient, Mailing, MailingAttempt
from .forms import RecipientForm, MailingForm
from .tasks import send_mailing_task


def home(request):
    """Главная страница со статистикой"""
    context = {
        'total_mailings': Mailing.objects.count(),
        'active_mailings': Mailing.objects.filter(status='running').count(),
        'unique_recipients': Recipient.objects.distinct().count(),
    }
    return render(request, 'home.html', context)


def mailing_attempts(request, mailing_id):
    """Просмотр попыток отправки для конкретной рассылки"""
    mailing = get_object_or_404(Mailing, pk=mailing_id)
    attempts = mailing.attempts.all().order_by('-timestamp')
    return render(request, 'mailing/mailing_attempts.html', {
        'mailing': mailing,
        'attempts': attempts
    })


# Recipient CRUD Views
def recipient_list(request):
    recipients = Recipient.objects.all()
    return render(request, 'mailing/recipient_list.html', {'recipients': recipients})


def recipient_create(request):
    if request.method == 'POST':
        form = RecipientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Получатель успешно создан')
            return redirect('mailing:recipient_list')
    else:
        form = RecipientForm()
    return render(request, 'mailing/recipient_form.html', {'form': form})


def recipient_update(request, pk):
    recipient = get_object_or_404(Recipient, pk=pk)
    if request.method == 'POST':
        form = RecipientForm(request.POST, instance=recipient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Получатель успешно обновлён')
            return redirect('mailing:recipient_list')
    else:
        form = RecipientForm(instance=recipient)
    return render(request, 'mailing/recipient_form.html', {'form': form})


def recipient_delete(request, pk):
    recipient = get_object_or_404(Recipient, pk=pk)
    if request.method == 'POST':
        recipient.delete()
        messages.success(request, 'Получатель успешно удалён')
        return redirect('mailing:recipient_list')
    return render(request, 'mailing/recipient_confirm_delete.html', {'recipient': recipient})


# Mailing CRUD Views
def mailing_list(request):
    mailings = Mailing.objects.all().order_by('-created_at')
    return render(request, 'mailing/mailing_list.html', {'mailings': mailings})


def mailing_create(request):
    if request.method == 'POST':
        form = MailingForm(request.POST)
        if form.is_valid():
            mailing = form.save()
            messages.success(request, 'Рассылка успешно создана')
            return redirect('mailing:mailing_list')
    else:
        form = MailingForm()
    return render(request, 'mailing/mailing_form.html', {'form': form})


def mailing_update(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    if request.method == 'POST':
        form = MailingForm(request.POST, instance=mailing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Рассылка успешно обновлена')
            return redirect('mailing:mailing_list')
    else:
        form = MailingForm(instance=mailing)
    return render(request, 'mailing/mailing_form.html', {'form': form})


def mailing_delete(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    if request.method == 'POST':
        mailing.delete()
        messages.success(request, 'Рассылка успешно удалена')
        return redirect('mailing:mailing_list')
    return render(request, 'mailing/mailing_confirm_delete.html', {'mailing': mailing})


def send_mailing(request, pk):
    """Запуск рассылки с проверкой статуса"""
    mailing = get_object_or_404(Mailing, pk=pk)

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