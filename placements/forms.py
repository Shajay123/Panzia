from django import forms
from .models import PlacementJob

class PlacementJobForm(forms.ModelForm):

    class Meta:

        model = PlacementJob

        fields = [
            "title",
            "description",
            "skills",
            "location",
            "salary",
            "experience_required",
            "job_type"
        ]

        widgets = {

            "title": forms.TextInput(attrs={
                "class":"form-control"
            }),

            "description": forms.Textarea(attrs={
                "class":"form-control",
                "rows":5
            }),

            "skills": forms.TextInput(attrs={
                "class":"form-control"
            }),

            "location": forms.TextInput(attrs={
                "class":"form-control"
            }),

            "salary": forms.TextInput(attrs={
                "class":"form-control"
            }),

            "experience_required": forms.TextInput(attrs={
                "class":"form-control"
            }),

            "job_type": forms.Select(attrs={
                "class":"form-control"
            })

        }