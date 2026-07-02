# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from startups.models import StartupProfile


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
            ('', 'Select Role'),
            ('super_admin', 'Super Admin'),
            ('startup_admin', 'Startup Admin'),
            ('startup_hr', 'Startup HR'),
            ('startup_manager', 'Startup Manager'),
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