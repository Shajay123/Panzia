from django import forms
from .models import (
    GSTFiling, TDSFiling, PFContribution, ESICContribution,
    MCAFiling, IncomeTaxFiling, ComplianceReminder
)

class GSTFilingForm(forms.ModelForm):
    class Meta:
        model = GSTFiling
        fields = [
            'return_type', 'month', 'year', 'turnover', 
            'tax_payable', 'due_date', 'status', 'remarks'
        ]
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }

class TDSFilingForm(forms.ModelForm):
    class Meta:
        model = TDSFiling
        fields = ['quarter', 'year', 'amount', 'due_date', 'status']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

class PFContributionForm(forms.ModelForm):
    class Meta:
        model = PFContribution
        fields = ['month', 'employee_count', 'amount', 'due_date', 'paid', 'payment_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ESICContributionForm(forms.ModelForm):
    class Meta:
        model = ESICContribution
        fields = ['month', 'amount', 'due_date', 'paid', 'payment_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }

class MCAFilingForm(forms.ModelForm):
    class Meta:
        model = MCAFiling
        fields = ['filing_name', 'due_date', 'status']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

class IncomeTaxFilingForm(forms.ModelForm):
    class Meta:
        model = IncomeTaxFiling
        fields = ['assessment_year', 'taxable_income', 'tax_amount', 'due_date', 'status']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ComplianceReminderForm(forms.ModelForm):
    class Meta:
        model = ComplianceReminder
        fields = ['title', 'due_date', 'completed']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }