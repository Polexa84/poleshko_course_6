from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .forms import RegisterForm, LoginForm
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.crypto import get_random_string

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.activation_key = get_random_string(32)
            user.save()

            subject = 'Подтверждение регистрации'
            message = f'Здравствуйте!  Для подтверждения регистрации перейдите по ссылке: {request.build_absolute_uri(reverse("users:confirm_email", args=[user.activation_key]))}'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [form.cleaned_data['email']]
            send_mail(subject, message, from_email, to_email, fail_silently=False)

            # messages.success(request, 'На ваш email отправлено письмо для подтверждения регистрации.')
            # return redirect('home')
            return render(request, 'users/registration_success.html', {'email': form.cleaned_data['email']})
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def confirm_email(request, token):
    try:
        user = User.objects.get(activation_key=token)
    except User.DoesNotExist:
        messages.error(request, 'Неверный токен подтверждения.')
        return redirect('home')

    if not user.is_active:
        user.is_active = True
        user.activation_key = None
        user.save()
        messages.success(request, 'Ваш email успешно подтвержден. Теперь вы можете войти.')
        return redirect('login')
    else:
        messages.info(request, 'Ваш email уже был подтвержден.')
        return redirect('home')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, form.error_messages['invalid_login'])
        else:
             for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')