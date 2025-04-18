from django.shortcuts import render, redirect, get_object_or_404
from .models import Recipient
from .forms import RecipientForm

def recipient_list(request):
    recipients = Recipient.objects.all()
    return render(request, 'mailing/recipient_list.html', {'recipients': recipients})

def recipient_create(request):
    if request.method == 'POST':
        form = RecipientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('recipient_list')
    else:
        form = RecipientForm()
    return render(request, 'mailing/recipient_form.html', {'form': form})

def recipient_update(request, pk):
    recipient = get_object_or_404(Recipient, pk=pk)
    if request.method == 'POST':
        form = RecipientForm(request.POST, instance=recipient)
        if form.is_valid():
            form.save()
            return redirect('recipient_list')
    else:
        form = RecipientForm(instance=recipient)
    return render(request, 'mailing/recipient_form.html', {'form': form})

def recipient_delete(request, pk):
    recipient = get_object_or_404(Recipient, pk=pk)
    if request.method == 'POST':
        recipient.delete()
        return redirect('recipient_list')
    return render(request, 'mailing/recipient_confirm_delete.html', {'recipient': recipient})