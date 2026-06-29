from django import forms
from .models import PortfolioProject


class PortfolioProjectForm(forms.ModelForm):

    class Meta:

        model = PortfolioProject

        fields = [

            "title",

            "project_type",

            "description",

            "skills",

            "project_url",

            "github_url",

            "image"

        ]


from django import forms
from .models import TalentProfile
from sprints.models import Skill


class TalentProfileForm(forms.ModelForm):

    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:

        model = TalentProfile

        fields = [

            "headline",

            "bio",

            "skills",

            "github",

            "linkedin",

            "portfolio",

            "profile_image"

        ]