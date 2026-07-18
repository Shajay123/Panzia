from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from startups.models import StartupProfile, StartupApplication


class RegisterForm(UserCreationForm):
    
    startup = forms.ModelChoiceField(
        queryset=StartupProfile.objects.filter(is_active=True),
        required=False,
        label='Startup (if applicable)',
        help_text='Select your startup if you are registering as a startup user'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'startup', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize role choices
        role_choices = [
            ('startup_hr', 'Startup HR'),
            ('employee', 'Employee'),
            ('talent', 'Talent'),
        ]
        self.fields['role'].choices = role_choices
        
        # Make startup required for startup roles
        self.fields['startup'].required = False

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        startup = cleaned_data.get('startup')
        
        # Validate that startup is provided for startup users
        if role in ['startup_admin', 'startup_hr', 'startup_manager', 'employee'] and not startup:
            raise forms.ValidationError({
                'startup': 'Please select a startup for this role.'
            })
        
        return cleaned_data


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
        if StartupProfile.objects.filter(company_name__iexact=company).exists():
            raise forms.ValidationError(
                "A startup with this name already exists. Please use a different name."
            )
        return company


class UserApprovalForm(forms.ModelForm):
    """Form for approving/rejecting users"""
    
    rejection_reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Reason for rejection...'}),
        required=False
    )
    
    class Meta:
        model = User
        fields = ['role']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [
            ('startup_admin', 'Startup Admin'),
            ('startup_hr', 'Startup HR'),
            ('startup_manager', 'Startup Manager'),
        ]
        self.fields['role'].required = True