from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    """Форма для создания и редактирования сообщений."""
    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }