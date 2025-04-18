from django.shortcuts import render, redirect, get_object_or_404
from .models import Message
from .forms import MessageForm

def message_list(request):
    """Отображает список сообщений."""
    messages = Message.objects.all()
    return render(request, 'postal_service/message_list.html', {'messages': messages})

def message_create(request):
    """Создает новое сообщение."""
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('postal_service:message_list')
    else:
        form = MessageForm()
    return render(request, 'postal_service/message_form.html', {'form': form})

def message_update(request, pk):
    """Редактирует существующее сообщение."""
    message = get_object_or_404(Message, pk=pk)
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return redirect('postal_service:message_list')
    else:
        form = MessageForm(instance=message)
    return render(request, 'postal_service/message_form.html', {'form': form})

def message_delete(request, pk):
    """Удаляет сообщение."""
    message = get_object_or_404(Message, pk=pk)
    if request.method == 'POST':
        message.delete()
        return redirect('postal_service:message_list')
    return render(request, 'postal_service/message_confirm_delete.html', {'message': message})