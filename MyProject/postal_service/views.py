from django.shortcuts import render, redirect, get_object_or_404
from .models import Message
from .forms import MessageForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages as django_messages
from users.utils import is_manager
import logging

logger = logging.getLogger(__name__)


@login_required
def message_list(request):
    """
    Отображает список сообщений.
    Менеджеры видят все сообщения, обычные пользователи - только свои.
    """
    try:
        if is_manager(request.user):
            messages = Message.objects.all().select_related('owner')
        else:
            messages = Message.objects.filter(owner=request.user)

        return render(request, 'postal_service/message_list.html', {
            'message_list': messages,
            'is_manager': is_manager(request.user)
        })
    except Exception as e:
        logger.error(f"Error fetching message list: {str(e)}")
        django_messages.error(request, 'Ошибка при загрузке списка сообщений')
        return redirect('home')


@login_required
def message_create(request):
    """
    Создает новое сообщение.
    Автоматически назначает текущего пользователя как владельца.
    """
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            try:
                message = form.save(commit=False)
                message.owner = request.user
                message.save()
                django_messages.success(request, 'Сообщение успешно создано')
                return redirect('postal_service:message_list')
            except Exception as e:
                logger.error(f"Error creating message: {str(e)}")
                django_messages.error(request, 'Ошибка при создании сообщения')
    else:
        form = MessageForm()

    return render(request, 'postal_service/message_form.html', {
        'form': form,
        'title': 'Создание сообщения'
    })


@login_required
def message_update(request, pk):
    """
    Редактирует существующее сообщение.
    Только владелец может редактировать, менеджеры не имеют доступа.
    """
    message = get_object_or_404(Message, pk=pk)

    if is_manager(request.user):
        django_messages.error(request, 'Менеджеры не могут редактировать сообщения')
        return redirect('postal_service:message_list')

    if message.owner != request.user:
        logger.warning(
            f"User {request.user} tried to edit message {pk} owned by {message.owner}"
        )
        raise PermissionDenied

    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            try:
                form.save()
                django_messages.success(request, 'Сообщение успешно обновлено')
                return redirect('postal_service:message_list')
            except Exception as e:
                logger.error(f"Error updating message {pk}: {str(e)}")
                django_messages.error(request, 'Ошибка при обновлении сообщения')
    else:
        form = MessageForm(instance=message)

    return render(request, 'postal_service/message_form.html', {
        'form': form,
        'title': 'Редактирование сообщения',
        'message': message
    })


@login_required
def message_delete(request, pk):
    """
    Удаляет сообщение.
    Только владелец может удалить, менеджеры не имеют доступа.
    """
    message = get_object_or_404(Message, pk=pk)

    if is_manager(request.user):
        django_messages.error(request, 'Менеджеры не могут удалять сообщения')
        return redirect('postal_service:message_list')

    if message.owner != request.user:
        logger.warning(
            f"User {request.user} tried to delete message {pk} owned by {message.owner}"
        )
        raise PermissionDenied

    if request.method == 'POST':
        try:
            message.delete()
            django_messages.success(request, 'Сообщение успешно удалено')
            return redirect('postal_service:message_list')
        except Exception as e:
            logger.error(f"Error deleting message {pk}: {str(e)}")
            django_messages.error(request, 'Ошибка при удалении сообщения')
            return redirect('postal_service:message_list')

    return render(request, 'postal_service/message_confirm_delete.html', {
        'message': message,
        'title': 'Подтверждение удаления'
    })