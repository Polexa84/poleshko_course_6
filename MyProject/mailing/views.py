from django.shortcuts import render, redirect, get_object_or_404
from .models import Recipient, Mailing
from .forms import RecipientForm, MailingForm

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
            return redirect('mailing:recipient_list')  # Use namespace
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
            return redirect('mailing:recipient_list')  # Use namespace
    else:
        form = RecipientForm(instance=recipient)
    return render(request, 'mailing/recipient_form.html', {'form': form})

def recipient_delete(request, pk):
    """Удаляет получателя."""
    recipient = get_object_or_404(Recipient, pk=pk)
    if request.method == 'POST':
        recipient.delete()
        return redirect('mailing:recipient_list')  # Use namespace
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
            return redirect('mailing:mailing_list')  # Use namespace
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
            return redirect('mailing:mailing_list')  # Use namespace
    else:
        form = MailingForm(instance=mailing)
    return render(request, 'mailing/mailing_form.html', {'form': form})

def mailing_delete(request, pk):
    """Удаляет рассылку."""
    mailing = get_object_or_404(Mailing, pk=pk)
    if request.method == 'POST':
        mailing.delete()
        return redirect('mailing:mailing_list')  # Use namespace
    return render(request, 'mailing/mailing_confirm_delete.html', {'mailing': mailing})