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

from django import forms
from .models import StartupApplication


class StartupApplicationForm(forms.ModelForm):
    """Form for startup registration application"""
    
    applicant_name = forms.CharField(max_length=255, required=True)
    applicant_email = forms.EmailField(required=True)
    applicant_phone = forms.CharField(max_length=15, required=False)
    
    class Meta:
        model = StartupApplication
        fields = [
            'company_name', 'tagline', 'website', 'industry', 'description', 'logo',
            'address', 'city', 'state', 'country',
            'applicant_name', 'applicant_email', 'applicant_phone'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def clean_applicant_email(self):
        email = self.cleaned_data.get('applicant_email')
        from accounts.models import User
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email is already registered. Please login or use a different email."
            )
        if StartupApplication.objects.filter(
            applicant_email=email, 
            status='pending'
        ).exists():
            raise forms.ValidationError(
                "An application with this email is already pending review."
            )
        return email
    
    def clean_company_name(self):
        company = self.cleaned_data.get('company_name')
        from .models import StartupProfile
        if StartupProfile.objects.filter(company_name__iexact=company).exists():
            raise forms.ValidationError(
                "A startup with this name already exists. Please use a different name."
            )
        return company