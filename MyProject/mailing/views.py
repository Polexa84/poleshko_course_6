from django.shortcuts import render, redirect, get_object_or_404
from .models import Recipient, Mailing, MailingAttempt  # Убедитесь, что MailingAttempt импортирован
from .forms import RecipientForm, MailingForm
from .tasks import send_mailing_task  # Импортируйте Celery задачу


# Главная страница
def home(request):
    total_mailings = Mailing.objects.count()
    active_mailings = Mailing.objects.filter(status='running').count()
    unique_recipients = Recipient.objects.distinct().count()

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_recipients': unique_recipients,
    }
    return render(request, 'home.html', context)


# Mailing Attempts View
def mailing_attempts(request, mailing_id):
    """
    View для отображения попыток рассылки для конкретной рассылки.
    """
    mailing = get_object_or_404(Mailing, pk=mailing_id)
    attempts = MailingAttempt.objects.filter(mailing=mailing).order_by('-attempt_time')
    return render(request, 'mailing/mailing_attempts.html', {'mailing': mailing, 'attempts': attempts})


# Recipient Views
def recipient_list(request):
    """Отображает список получателей."""
    recipients = Recipient.objects.all()
    return render(request, 'mailing/recipient_list.html', {'recipients': recipients})


def recipient_create(request):
    """Создает нового получателя."""
    if request.method == 'POST':
        form = RecipientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('mailing:recipient_list')  # Используйте пространство имен
    else:
        form = RecipientForm()
    return render(request, 'mailing/recipient_form.html', {'form': form})


def recipient_update(request, pk):
    """Редактирует существующего получателя."""
    recipient = get_object_or_404(Recipient, pk=pk)
    if request.method == 'POST':
        form = RecipientForm(request.POST, instance=recipient)
        if form.is_valid():
            form.save()
            return redirect('mailing:recipient_list')  # Используйте пространство имен
    else:
        form = RecipientForm(instance=recipient)
    return render(request, 'mailing/recipient_form.html', {'form': form})


def recipient_delete(request, pk):
    """Удаляет получателя."""
    recipient = get_object_or_404(Recipient, pk=pk)
    if request.method == 'POST':
        recipient.delete()
        return redirect('mailing:recipient_list')  # Используйте пространство имен
    return render(request, 'mailing/recipient_confirm_delete.html', {'recipient': recipient})


# Mailing Views
def mailing_list(request):
    """Отображает список рассылок."""
    mailings = Mailing.objects.all()
    return render(request, 'mailing/mailing_list.html', {'mailings': mailings})


def mailing_create(request):
    """Создает новую рассылку."""
    if request.method == 'POST':
        form = MailingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('mailing:mailing_list')  # Используйте пространство имен
    else:
        form = MailingForm()
    return render(request, 'mailing/mailing_form.html', {'form': form})


def mailing_update(request, pk):
    """Редактирует существующую рассылку."""
    mailing = get_object_or_404(Mailing, pk=pk)
    if request.method == 'POST':
        form = MailingForm(request.POST, instance=mailing)
        if form.is_valid():
            form.save()
            return redirect('mailing:mailing_list')  # Используйте пространство имен
    else:
        form = MailingForm(instance=mailing)
    return render(request, 'mailing/mailing_form.html', {'form': form})


def mailing_delete(request, pk):
    """Удаляет рассылку."""
    mailing = get_object_or_404(Mailing, pk=pk)
    if request.method == 'POST':
        mailing.delete()
        return redirect('mailing:mailing_list')  # Используйте пространство имен
    return render(request, 'mailing/mailing_confirm_delete.html', {'mailing': mailing})


def send_mailing(request, pk):
    """Отправляет рассылку по требованию."""
    mailing = get_object_or_404(Mailing, pk=pk)

    # Проверяем статус рассылки
    if mailing.status != 'completed':
        # Запускаем Celery задачу для отправки рассылки
        send_mailing_task.delay(mailing.pk)

        mailing.status = 'started'
        mailing.save()

        return redirect('mailing:mailing_list')  # Перенаправляем на страницу списка рассылок
    else:
        # Обрабатываем ситуацию с уже отправленной рассылкой
        return render(request, 'mailing/mailing_already_sent.html', {'mailing': mailing})