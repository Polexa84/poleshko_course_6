from django.shortcuts import render, redirect, get_object_or_404
from .models import Message
from .forms import MessageForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages as django_messages  # Переименовываем для ясности
from users.utils import is_manager

@login_required
def message_list(request):
    """Отображает список сообщений."""
    if is_manager(request.user):
        message_list = Message.objects.all()  # Переименовываем переменную
    else:
        message_list = Message.objects.filter(owner=request.user)
    return render(request, 'postal_service/message_list.html', {'message_list': message_list})

@login_required
def message_create(request):
    """Создает новое сообщение."""
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.owner = request.user
            message.save()
            django_messages.success(request, 'Сообщение успешно создано')  # Используем переименованное
            return redirect('postal_service:message_list')
    else:
        form = MessageForm()
    return render(request, 'postal_service/message_form.html', {'form': form})

@login_required
def message_update(request, pk):
    """Редактирует существующее сообщение."""
    message = get_object_or_404(Message, pk=pk)

    if is_manager(request.user):
        django_messages.error(request, 'Менеджеры не могут редактировать сообщения')  # Используем переименованное
        return redirect('postal_service:message_list')

    if message.owner != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            django_messages.success(request, 'Сообщение успешно обновлено')  # Используем переименованное
            return redirect('postal_service:message_list')
    else:
        form = MessageForm(instance=message)
    return render(request, 'postal_service/message_form.html', {'form': form})

@login_required
def message_delete(request, pk):
    """Удаляет сообщение."""
    message = get_object_or_404(Message, pk=pk)

    if is_manager(request.user):
        django_messages.error(request, 'Менеджеры не могут удалять сообщения')  # Используем переименованное
        return redirect('postal_service:message_list')

    if message.owner != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        message.delete()
        django_messages.success(request, 'Сообщение успешно удалено')  # Используем переименованное
        return redirect('postal_service:message_list')
    return render(request, 'postal_service/message_confirm_delete.html', {'message': message})