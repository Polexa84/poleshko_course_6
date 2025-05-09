from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    """Форма для создания и редактирования сообщений."""
    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите тему сообщения'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Введите текст сообщения'
            }),
        }
        labels = {
            'subject': 'Тема сообщения',
            'body': 'Текст сообщения'
        }
        help_texts = {
            'subject': 'Кратко опишите суть сообщения',
            'body': 'Полный текст, который будет отправлен получателям'
        }