from django import forms
from .models import Interview


class InterviewForm(forms.ModelForm):

    class Meta:

        model = Interview

        fields = [

            "interview_date",
            "meeting_link",
            "notes"

        ]

        widgets = {

            "interview_date":
                forms.DateTimeInput(
                    attrs={
                        "type":"datetime-local"
                    }
                )

        }