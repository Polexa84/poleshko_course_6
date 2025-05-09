from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserChangeForm
)
from django.utils.translation import gettext_lazy as _
from .models import User


class UserProfileForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'avatar')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': _('Логин'),
            'email': _('Email'),
            'first_name': _('Имя'),
            'last_name': _('Фамилия'),
            'phone': _('Телефон'),
            'avatar': _('Аватар'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    error_messages = {
        'password_too_short': _("Ваш пароль слишком короткий."),
        'password_too_common': _("Ваш пароль слишком распространен."),
        'password_entirely_numeric': _("Ваш пароль не может состоять только из цифр."),
        'invalid_email': _("Введите правильный адрес электронной почты."),
        'unique_email': _("Пользователь с таким email уже существует.")
    }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                self.error_messages['unique_email'],
                code='unique_email',
            )
        return email

class LoginForm(AuthenticationForm):
    error_messages = {
        'invalid_login': _(
            "Пожалуйста, введите правильные имя пользователя и пароль. "
            "Оба поля могут быть чувствительны к регистру."
        ),
        'inactive': _("Ваш аккаунт не активирован. Пожалуйста, проверьте свою почту для подтверждения."),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control'})

class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })

    error_messages = {
        'password_mismatch': _("Пароли не совпадают."),
        'password_too_short': _("Пароль слишком короткий."),
        'password_too_common': _("Пароль слишком распространен."),
        'password_entirely_numeric': _("Пароль не может состоять только из цифр."),
    }