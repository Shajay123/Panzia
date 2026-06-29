from django import forms
from .models import Sprint


class SprintForm(forms.ModelForm):

    class Meta:

        model = Sprint

        fields = [
            'title',
            'description',
            'domain',
            'category',
            'required_skills',
            'deadline',
            'max_contributors',
            'status',
        ]

        widgets = {

            'deadline': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            ),

            'required_skills': forms.SelectMultiple(
                attrs={
                    'class': 'form-control'
                }
            ),
        }


from .models import Task

class TaskForm(forms.ModelForm):

    class Meta:
        model = Task

        fields = [
            'title',
            'description',
            'assigned_to',
            'deadline'
        ]

        widgets = {
            'deadline': forms.DateInput(
                attrs={'type': 'date'}
            )
        }