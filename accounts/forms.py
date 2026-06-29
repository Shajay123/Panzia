from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'role',
            'password1',
            'password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            'username': 'Enter username',
            'email': 'Enter email',
            'role': 'Select role',
            'password1': 'Create password',
            'password2': 'Confirm password'
        }

        for name, field in self.fields.items():

            field.widget.attrs.update({
                'class': 'form-control-custom'
            })

            if name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[name]