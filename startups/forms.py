from django import forms
from .models import StartupProfile

class StartupProfileForm(forms.ModelForm):

    class Meta:
        model = StartupProfile

        fields = [
            'company_name',
            'tagline',
            'website',
            'industry',
            'description',
            'logo',
        ]

        widgets = {
            'company_name': forms.TextInput(attrs={
                'placeholder': 'Enter company name'
            }),
            'tagline': forms.TextInput(attrs={
                'placeholder': 'Your startup tagline'
            }),
            'industry': forms.TextInput(attrs={
                'placeholder': 'Technology, Healthcare, FinTech...'
            }),
            'website': forms.URLInput(attrs={
                'placeholder': 'https://yourstartup.com'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Describe your startup vision...'
            }),
        }