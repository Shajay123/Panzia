from django import forms
from .models import PlacementJob


class PlacementJobForm(forms.ModelForm):
    class Meta:
        model = PlacementJob
        fields = [
            'title',
            'description',
            'skills',
            'location',
            'salary',
            'job_type',
            'experience_required',
            'status'
        ]
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe the role, responsibilities, and requirements...',
                'rows': 5
            }),
            'skills': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Python, React, AWS, Django...'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Senior Software Engineer'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., San Francisco, CA or Remote'
            }),
            'salary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., $50,000 - $70,000 or Negotiable'
            }),
            'job_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'experience_required': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 3+ years, Entry Level, Senior'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'title': 'Job Title',
            'description': 'Description',
            'skills': 'Required Skills',
            'location': 'Location',
            'salary': 'Salary',
            'job_type': 'Job Type',
            'experience_required': 'Experience Required',
            'status': 'Status'
        }
        help_texts = {
            'skills': 'List skills separated by commas',
            'salary': 'Enter salary range or "Negotiable"'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set status choices with proper labels
        self.fields['status'].choices = [
            ('Open', 'Open'),
            ('Pending', 'Pending'),
            ('Closed', 'Closed'),
        ]
        # Make status optional with default
        self.fields['status'].required = False
        self.fields['status'].initial = 'Open'