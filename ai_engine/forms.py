from django import forms
from .models import CareerGoal

class CareerGoalForm(forms.ModelForm):

    class Meta:

        model = CareerGoal

        fields = ["goal"]

        widgets = {

            "goal": forms.Select(
                choices=[

                    ("AI Engineer","AI Engineer"),

                    ("Data Scientist","Data Scientist"),

                    ("Full Stack Developer","Full Stack Developer"),

                    ("Backend Developer","Backend Developer"),

                    ("DevOps Engineer","DevOps Engineer"),

                    ("Product Manager","Product Manager")

                ]
            )

        }