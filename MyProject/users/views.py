from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm, LoginForm
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from .forms import CustomPasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from .forms import UserProfileForm
from django.contrib.auth.decorators import login_required
from .models import User

class MyPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'users/password_reset_form.html'
    success_url = '/users/password_reset/done/'

    def form_valid(self, form):
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.get_email_from(),
            'request': self.request,
            'html_email_template_name': 'users/password_reset_email.html',  # Указываем HTML шаблон
            'email_template_name': 'users/password_reset_email.txt',  # Указываем TXT шаблон (если есть)
            'extra_email_context': { # Добавляем extra_email_context
                'reset_url': self.request.build_absolute_uri(
                    reverse(
                        'users:password_reset_confirm',
                        kwargs={'uidb64': form.request.POST['email'].encode(), 'token': form.token_generator.make_token(self.request.user)}
                    )
                )
            }
        }
        form.save(**opts)
        return super().form_valid(form)

    def get_email_from(self):
        return settings.DEFAULT_FROM_EMAIL

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            activation_url = request.build_absolute_uri(
                reverse("users:confirm_email", args=[uid, token])
            )

            subject = 'Подтверждение регистрации'
            message = f'Для подтверждения email перейдите по ссылке:\n{activation_url}'
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            # Только здесь добавляем сообщение (без дублирования в шаблоне)
            messages.info(request, 'Письмо для подтверждения регистрации отправлено на ваш email.')
            return redirect('login')

    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})
def confirm_email(request, uidb64, token):
    try:
        # Декодируем uidb64 и получаем ID пользователя
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        # Проверяем токен на валидность
        if default_token_generator.check_token(user, token):
            if not user.is_active:
                user.is_active = True  # Активируем аккаунт пользователя
                user.save()
                messages.success(request, 'Email подтверждён! Теперь можно войти.')
                return redirect('login')
            else:
                messages.info(request, 'Ваш аккаунт уже активирован.')
        else:
            messages.error(request, 'Неверная ссылка подтверждения.')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, 'Ошибка активации. Неверный токен или пользователь.')

    return redirect('home')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)  # Исправлено здесь
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    else:  # Этот else должен быть правильно выровнен
        form = LoginForm()  # Инициализация формы для GET-запросов

    return render(request, 'users/login.html', {'form': form})

@ensure_csrf_cookie
def logout_view(request):
    logout(request)
    messages.success(request, 'Вы вышли из системы.')  # Сообщение об успешном выходе
    return redirect('home')

@login_required
def profile_view(request):
    """Контроллер просмотра профиля"""
    return render(request, 'users/profile.html', {'user': request.user})


@login_required
def profile_edit(request):
    """Контроллер редактирования профиля"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'users/profile_edit.html', {'form': form})