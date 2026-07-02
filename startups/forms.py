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
            'address',
            'city',
            'state',
            'country',
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'placeholder': 'Enter company name',
                'class': 'form-control'
            }),
            'tagline': forms.TextInput(attrs={
                'placeholder': 'Your startup tagline',
                'class': 'form-control'
            }),
            'industry': forms.TextInput(attrs={
                'placeholder': 'Technology, Healthcare, FinTech...',
                'class': 'form-control'
            }),
            'website': forms.URLInput(attrs={
                'placeholder': 'https://yourstartup.com',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Describe your startup vision...',
                'rows': 5,
                'class': 'form-control'
            }),
            'address': forms.Textarea(attrs={
                'placeholder': 'Company address...',
                'rows': 3,
                'class': 'form-control'
            }),
            'city': forms.TextInput(attrs={
                'placeholder': 'City',
                'class': 'form-control'
            }),
            'state': forms.TextInput(attrs={
                'placeholder': 'State',
                'class': 'form-control'
            }),
            'country': forms.TextInput(attrs={
                'placeholder': 'Country',
                'class': 'form-control'
            }),
        }