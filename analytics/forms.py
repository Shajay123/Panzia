from django import forms
from .models import (
    DailySnapshot, WeeklyReport, MonthlyReport, 
    RunwayCalculation, BurnRateRecord, InvestorReport,
    LeaderboardEntry
)
from startups.models import StartupProfile


class DailySnapshotForm(forms.ModelForm):
    class Meta:
        model = DailySnapshot
        fields = [
            'total_employees', 'active_employees', 'new_employees',
            'total_payroll', 'total_revenue', 'total_expenses',
            'present_count', 'absent_count', 'on_leave_count',
            'avg_performance_rating', 'completed_reviews', 'pending_reviews'
        ]
        widgets = {
            'total_payroll': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_revenue': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_expenses': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'avg_performance_rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '5'}),
        }


class WeeklyReportForm(forms.ModelForm):
    class Meta:
        model = WeeklyReport
        fields = [
            'week_start', 'week_end', 'week_number', 'year',
            'total_employees', 'new_employees',
            'total_payroll', 'total_revenue', 'total_expenses',
            'avg_attendance_rate', 'total_absent_days', 'total_leave_days',
            'avg_performance_rating', 'reviews_completed'
        ]
        widgets = {
            'week_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'week_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'week_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class MonthlyReportForm(forms.ModelForm):
    class Meta:
        model = MonthlyReport
        fields = [
            'month', 'year',
            'total_employees', 'new_employees',
            'total_payroll', 'total_revenue', 'total_expenses',
            'avg_attendance_rate', 'total_absent_days', 'total_leave_days',
            'avg_performance_rating', 'reviews_completed',
            'employee_growth_rate', 'revenue_growth_rate'
        ]
        widgets = {
            'month': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('January', 'January'), ('February', 'February'), ('March', 'March'),
                ('April', 'April'), ('May', 'May'), ('June', 'June'),
                ('July', 'July'), ('August', 'August'), ('September', 'September'),
                ('October', 'October'), ('November', 'November'), ('December', 'December')
            ]),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class RunwayCalculationForm(forms.ModelForm):
    class Meta:
        model = RunwayCalculation
        fields = ['current_cash', 'monthly_burn_rate', 'monthly_revenue', 'funding_rounds']
        widgets = {
            'current_cash': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'monthly_burn_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'monthly_revenue': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'funding_rounds': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter funding rounds as JSON'})
        }
    
    def clean_funding_rounds(self):
        data = self.cleaned_data.get('funding_rounds')
        if data and isinstance(data, str):
            try:
                import json
                return json.loads(data)
            except json.JSONDecodeError:
                raise forms.ValidationError("Invalid JSON format")
        return data


class BurnRateRecordForm(forms.ModelForm):
    class Meta:
        model = BurnRateRecord
        fields = [
            'month', 'year',
            'total_expenses', 'total_revenue', 'burn_rate', 'cash_balance',
            'payroll_expenses', 'operational_expenses', 'marketing_expenses',
            'infrastructure_expenses', 'other_expenses'
        ]
        widgets = {
            'month': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('January', 'January'), ('February', 'February'), ('March', 'March'),
                ('April', 'April'), ('May', 'May'), ('June', 'June'),
                ('July', 'July'), ('August', 'August'), ('September', 'September'),
                ('October', 'October'), ('November', 'November'), ('December', 'December')
            ]),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_expenses': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_revenue': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'burn_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cash_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class InvestorReportForm(forms.ModelForm):
    class Meta:
        model = InvestorReport
        fields = [
            'report_title', 'report_date',
            'total_employees', 'total_revenue', 'total_expenses',
            'cash_balance', 'runway_months',
            'key_achievements', 'key_challenges', 'next_quarter_goals',
            'funds_raised', 'valuation', 'is_published'
        ]
        widgets = {
            'report_title': forms.TextInput(attrs={'class': 'form-control'}),
            'report_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'key_achievements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'key_challenges': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'next_quarter_goals': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )