from django import forms
from .models import Recipient

class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ['email', 'full_name', 'comment']
        help_texts = {
            'email': 'Введите корректный email адрес.',
            'full_name': 'Введите ваше полное имя.',
            'comment': 'Здесь можно оставить любой комментарий.',
        }
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
        }