from django import forms
from django.utils import timezone
from .models import Recipient, Mailing
from postal_service.models import Message
from django.contrib.auth import get_user_model

User = get_user_model()


class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ['email', 'full_name', 'comment']
        help_texts = {
            'email': 'Введите корректный email адрес.',
            'full_name': 'Введите полное имя.',
            'comment': 'Здесь можно оставить любой комментарий.',
        }
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@domain.com'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванов Иван Иванович'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Дополнительная информация о получателе'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.owner = self.user
        if commit:
            instance.save()
        return instance



class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['start_time', 'end_time', 'status', 'message', 'recipients']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
                'choices': [
                    ('Создана', 'Создана'),
                    ('Запущена', 'Запущена'),
                    ('Завершена', 'Завершена')
                ]
            }),
            'message': forms.Select(attrs={
                'class': 'form-control'
            }),
            'recipients': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'start_time': 'Дата и время первой отправки',
            'end_time': 'Дата и время окончания отправки',
            'status': 'Статус',
            'message': 'Сообщение',
            'recipients': 'Получатели'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['recipients'].queryset = Recipient.objects.filter(owner=self.user)
            self.fields['message'].queryset = Message.objects.filter(owner=self.user)

        now = timezone.now().strftime('%Y-%m-%dT%H:%M')
        self.fields['start_time'].widget.attrs['min'] = now
        self.fields['end_time'].widget.attrs['min'] = now

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError(
                "Время окончания должно быть позже времени начала"
            )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.owner = self.user
            instance.status = 'created'  # Устанавливаем статус по умолчанию
        if commit:
            instance.save()
            self.save_m2m()  # Сохраняем ManyToMany отношения
        return instance