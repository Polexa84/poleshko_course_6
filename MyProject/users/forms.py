from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm # Import AuthenticationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

class RegisterForm(UserCreationForm):
    email = forms.EmailField(label=_("Email"))

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    error_messages = {
        'password_too_short': _("Ваш пароль слишком короткий."),
        'password_too_common': _("Ваш пароль слишком распространен."),
        'password_entirely_numeric': _("Ваш пароль не может состоять только из цифр."),
    }


class LoginForm(AuthenticationForm):  # Create a LoginForm
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Имя пользователя'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Пароль'})