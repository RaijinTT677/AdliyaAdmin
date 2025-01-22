from django import forms
from .models import Content

class ContentForm(forms.ModelForm):
    format = forms.ChoiceField(choices=Content.FORMAT_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Content
        fields = ['name', 'file', 'image', 'format', 'is_active']
        labels = {
            'name': 'Название',
            'file': 'Файл',
            'format': 'Формат',
            'is_active': 'Активен',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
