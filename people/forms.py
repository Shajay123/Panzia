from django import forms

from accounts.models import User

from .models import (
    DepartmentTimingConfig,
    Employee,
    Department,
    Attendance,
    ExitRequest,
    LeaveRequest,
    Payroll,
    PerformanceReview,
    EmployeeDocument,
    Holiday,
    Payslip,
)


# =====================================================
# EMPLOYEE
# =====================================================

from django import forms

from .models import Employee, Department


# forms.py - EmployeeForm

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "department",
            "manager",
            "employee_id",
            "designation",
            "employment_type",
            "status",
            "hire_source",
            "work_mode",
            "phone",
            "emergency_contact",
            "joining_date",
            "probation_end",
            "confirmation_date",
            "salary",
            "is_payroll_enabled",
            "is_active",  # <-- Make sure this is here
            "profile_image",
            "notes",
        ]
        widgets = {
            "joining_date": forms.DateInput(attrs={"type": "date"}),
            "probation_end": forms.DateInput(attrs={"type": "date"}),
            "confirmation_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4, "placeholder": "Additional notes..."}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_payroll_enabled": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, startup=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Bootstrap styling
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({"class": "form-check-input"})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({"class": "form-control"})
            else:
                field.widget.attrs.update({"class": "form-control"})

        # Department only for this startup
        if startup:
            self.fields["department"].queryset = Department.objects.filter(startup=startup)
            self.fields["manager"].queryset = Employee.objects.filter(startup=startup)

        # Set default value for is_active
        if 'is_active' in self.fields:
            self.fields['is_active'].initial = True

        # Placeholders
        self.fields["employee_id"].widget.attrs["placeholder"] = "EMP0001"
        self.fields["designation"].widget.attrs["placeholder"] = "Software Engineer"
        self.fields["phone"].widget.attrs["placeholder"] = "+91 9876543210"
        self.fields["emergency_contact"].widget.attrs["placeholder"] = "+91 9876543210"
        self.fields["salary"].widget.attrs["placeholder"] = "50000"

# =====================================================
# DEPARTMENT
# =====================================================

class DepartmentForm(forms.ModelForm):

    class Meta:

        model = Department

        fields = [

            "name",
            "code",
            "description",

        ]

        widgets = {

            "description": forms.Textarea(
                attrs={
                    "rows": 3
                }
            )

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field in self.fields.values():

            field.widget.attrs.update({
                "class": "form-control"
            })


# =====================================================
# ATTENDANCE
# =====================================================

# forms.py - AttendanceForm (Final Version)

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = "__all__"
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "check_in": forms.TimeInput(attrs={"type": "time"}),
            "check_out": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        # Extract startup from kwargs
        self.startup = kwargs.pop('startup', None)
        
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs.update({
                    "class": "form-control"
                })

        # Filter employees by startup
        if self.startup:
            self.fields["employee"].queryset = Employee.objects.filter(
                startup=self.startup,
                is_active=True
            ).select_related("user")
        else:
            self.fields["employee"].queryset = Employee.objects.none()
        
        # Make employee field required
        self.fields["employee"].required = True
        
        # IMPORTANT: REMOVE the disabled line below
        # self.fields["employee"].disabled = True  # <-- DELETE THIS LINE!
# forms.py - Complete Leave Forms with Startup Filtering

from django import forms
from django.core.exceptions import ValidationError
from .models import LeaveRequest


class LeaveRequestForm(forms.ModelForm):

    class Meta:

        model = LeaveRequest

        fields = "__all__"

        widgets = {

            "from_date": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),

            "to_date": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),

            "reason": forms.Textarea(
                attrs={
                    "rows": 4
                }
            ),

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field in self.fields.values():

            field.widget.attrs.update({

                "class": "form-control"

            })

    def clean(self):

        cleaned_data = super().clean()

        from_date = cleaned_data.get("from_date")
        to_date = cleaned_data.get("to_date")

        if from_date and to_date:

            if from_date > to_date:

                raise ValidationError(
                    "From Date cannot be greater than To Date."
                )

        return cleaned_data


from django import forms
from .models import Employee


class LeaveRequestFilterForm(forms.Form):

    employee = forms.ModelChoiceField(

        queryset=Employee.objects.none(),

        required=False,

        empty_label="All Employees"

    )

    status = forms.ChoiceField(

        required=False,

        choices=[

            ("", "All Status"),

            ("Pending", "Pending"),

            ("Approved", "Approved"),

            ("Rejected", "Rejected"),

        ]

    )

    leave_type = forms.CharField(

        required=False

    )

    from_date = forms.DateField(

        required=False,

        widget=forms.DateInput(
            attrs={
                "type": "date"
            }
        )

    )

    to_date = forms.DateField(

        required=False,

        widget=forms.DateInput(
            attrs={
                "type": "date"
            }
        )

    )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field in self.fields.values():

            field.widget.attrs.update({

                "class": "form-control"

            })
    

    
# forms.py - Completely Fixed

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Payroll, Employee


class PayrollForm(forms.ModelForm):
    
    class Meta:
        model = Payroll
        fields = [
            'employee',
            'month',
            'year',
            'basic_salary',
            'allowances',
            'deductions',
            'net_salary',
            'paid',
            'paid_date'
        ]
        widgets = {
            'employee': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'month': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'year': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'basic_salary': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'placeholder': '0.00',
                    'min': '0'
                }
            ),
            'allowances': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'placeholder': '0.00',
                    'min': '0'
                }
            ),
            'deductions': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'placeholder': '0.00',
                    'min': '0'
                }
            ),
            'net_salary': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'readonly': True,
                    'placeholder': 'Auto-calculated'
                }
            ),
            'paid': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            ),
            'paid_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
        }
        labels = {
            'employee': 'Employee',
            'month': 'Month',
            'year': 'Year',
            'basic_salary': 'Basic Salary',
            'allowances': 'Allowances',
            'deductions': 'Deductions',
            'net_salary': 'Net Salary',
            'paid': 'Paid',
            'paid_date': 'Paid Date',
        }
        help_texts = {
            'basic_salary': 'Base salary amount.',
            'allowances': 'Additional allowances (HRA, DA, etc.).',
            'deductions': 'Deductions (tax, insurance, etc.).',
            'net_salary': 'Calculated automatically (Basic + Allowances - Deductions).',
        }

    def __init__(self, *args, **kwargs):
        # Extract startup from kwargs
        self.startup = kwargs.pop('startup', None)
        
        super().__init__(*args, **kwargs)
        
        # Set month choices
        month_choices = [
            ('', 'Select Month'),
            ('January', 'January'),
            ('February', 'February'),
            ('March', 'March'),
            ('April', 'April'),
            ('May', 'May'),
            ('June', 'June'),
            ('July', 'July'),
            ('August', 'August'),
            ('September', 'September'),
            ('October', 'October'),
            ('November', 'November'),
            ('December', 'December'),
        ]
        self.fields['month'].choices = month_choices
        
        # Set year choices
        current_year = timezone.now().year
        year_choices = [('', 'Select Year')] + [(year, str(year)) for year in range(current_year - 5, current_year + 3)]
        self.fields['year'].choices = year_choices
        
        # IMPORTANT: Set employee queryset based on startup
        if self.startup:
            self.fields['employee'].queryset = Employee.objects.filter(
                startup=self.startup,
                is_active=True
            ).select_related('user')
        else:
            self.fields['employee'].queryset = Employee.objects.none()
        
        # Add form-control class to all fields
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs.update({
                    'class': 'form-control'
                })
        
        # Make fields required
        self.fields['employee'].required = True
        self.fields['month'].required = True
        self.fields['year'].required = True
        self.fields['basic_salary'].required = True
        
        # If instance exists and is paid, disable editing
        if self.instance and self.instance.pk and self.instance.paid:
            for field in ['basic_salary', 'allowances', 'deductions', 'net_salary', 'employee', 'month', 'year']:
                if field in self.fields:
                    self.fields[field].widget.attrs['readonly'] = True
                    self.fields[field].widget.attrs['disabled'] = True
                    self.fields[field].required = False

    def clean(self):
        cleaned_data = super().clean()
        
        basic = cleaned_data.get('basic_salary') or 0
        allowance = cleaned_data.get('allowances') or 0
        deduction = cleaned_data.get('deductions') or 0
        
        # Validate basic salary
        if basic < 0:
            raise ValidationError({
                'basic_salary': 'Basic salary cannot be negative.'
            })
        
        # Validate allowances
        if allowance < 0:
            raise ValidationError({
                'allowances': 'Allowances cannot be negative.'
            })
        
        # Validate deductions
        if deduction < 0:
            raise ValidationError({
                'deductions': 'Deductions cannot be negative.'
            })
        
        # Calculate net salary
        net = basic + allowance - deduction
        
        # Validate net salary
        if net < 0:
            raise ValidationError(
                'Net Salary cannot be negative. Please check allowances and deductions.'
            )
        
        cleaned_data['net_salary'] = net
        
        return cleaned_data

    def clean_employee(self):
        employee = self.cleaned_data.get('employee')
        if not employee:
            raise ValidationError('Please select an employee.')
        return employee

    def clean_month(self):
        month = self.cleaned_data.get('month')
        if not month or month == '':
            raise ValidationError('Please select a month.')
        return month

    def clean_year(self):
        year = self.cleaned_data.get('year')
        if not year:
            raise ValidationError('Please select a year.')
        return year

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Calculate net salary
        instance.net_salary = instance.basic_salary + instance.allowances - instance.deductions
        
        # If paid, set paid date
        if instance.paid and not instance.paid_date:
            instance.paid_date = timezone.now().date()
        
        if commit:
            instance.save()
        return instance


class PayrollFilterForm(forms.Form):
    """Form for filtering payroll records"""
    
    def __init__(self, *args, startup=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set employee queryset based on startup
        if startup:
            self.fields['employee'].queryset = Employee.objects.filter(
                startup=startup,
                is_active=True
            ).select_related('user')
        else:
            self.fields['employee'].queryset = Employee.objects.none()
        
        # Set year choices
        current_year = timezone.now().year
        year_choices = [('', 'All Years')] + [(year, str(year)) for year in range(current_year - 5, current_year + 3)]
        self.fields['year'].choices = year_choices
        
        # Add form-control class to all fields
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs.update({
                    'class': 'form-control'
                })
    
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.none(),
        required=False,
        empty_label="All Employees",
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )
    month = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Months'),
            ('January', 'January'),
            ('February', 'February'),
            ('March', 'March'),
            ('April', 'April'),
            ('May', 'May'),
            ('June', 'June'),
            ('July', 'July'),
            ('August', 'August'),
            ('September', 'September'),
            ('October', 'October'),
            ('November', 'November'),
            ('December', 'December'),
        ],
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )
    year = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )
    status = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Status'),
            ('paid', '✅ Paid'),
            ('pending', '⏳ Pending'),
        ],
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )

# =====================================================
# EMPLOYEE DOCUMENT
# =====================================================

class EmployeeDocumentForm(forms.ModelForm):

    class Meta:

        model = EmployeeDocument

        fields = "__all__"

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field in self.fields.values():

            field.widget.attrs.update({
                "class": "form-control"
            })


# forms.py - Holiday forms

class HolidayForm(forms.ModelForm):
    
    class Meta:
        model = Holiday
        fields = ['name', 'date', 'holiday_type', 'description', 'is_company_holiday']
        widgets = {
            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter holiday name'
                }
            ),
            'holiday_type': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'rows': 4,
                    'class': 'form-control',
                    'placeholder': 'Enter holiday description...'
                }
            ),
            'is_company_holiday': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            ),
        }
        labels = {
            'name': 'Holiday Name',
            'date': 'Date',
            'holiday_type': 'Holiday Type',
            'description': 'Description',
            'is_company_holiday': 'Company Holiday',
        }
        help_texts = {
            'name': 'Enter the name of the holiday.',
            'date': 'Select the date of the holiday.',
            'holiday_type': 'Select the type of holiday.',
            'description': 'Add any additional details about the holiday.',
            'is_company_holiday': 'Check if this is a company-wide holiday.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add form-control class to all fields
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs.update({
                    'class': 'form-control'
                })
        
        # Make required fields
        self.fields['name'].required = True
        self.fields['date'].required = True
        self.fields['holiday_type'].required = True
        
        # Set holiday type choices
        holiday_type_choices = [
            ('', 'Select Holiday Type'),
            ('National', 'National Holiday'),
            ('Public', 'Public Holiday'),
            ('Company', 'Company Holiday'),
            ('Festival', 'Festival'),
            ('Optional', 'Optional Holiday'),
        ]
        self.fields['holiday_type'].choices = holiday_type_choices

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        
        # Validate date (cannot be in the past for new holidays)
        if date and not self.instance.pk:
            from django.utils import timezone
            if date < timezone.now().date():
                raise ValidationError('Holiday date cannot be in the past.')
        
        return cleaned_data


class HolidayFilterForm(forms.Form):
    """Form for filtering holidays"""
    
    holiday_type = forms.ChoiceField(
        choices=[
            ('', 'All Types'),
            ('National', 'National Holiday'),
            ('Public', 'Public Holiday'),
            ('Company', 'Company Holiday'),
            ('Festival', 'Festival'),
            ('Optional', 'Optional Holiday'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    year = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    status = forms.ChoiceField(
        choices=[
            ('', 'All Status'),
            ('upcoming', 'Upcoming'),
            ('past', 'Past'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set year choices
        from django.utils import timezone
        current_year = timezone.now().year
        year_choices = [('', 'All Years')] + [(year, str(year)) for year in range(current_year - 2, current_year + 3)]
        self.fields['year'].choices = year_choices
        
        # Add form-control class
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs.update({
                    'class': 'form-control'
                })


# =====================================================
# PAYSLIP
# =====================================================

# forms.py - Add PayslipForm

class PayslipForm(forms.ModelForm):
    
    class Meta:
        model = Payslip
        fields = ['payroll', 'pdf']
        widgets = {
            'payroll': forms.Select(attrs={
                'class': 'form-control'
            }),
            'pdf': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
        }
        labels = {
            'payroll': 'Payroll Record',
            'pdf': 'PDF File',
        }
        help_texts = {
            'payroll': 'Select the payroll record for this payslip.',
            'pdf': 'Upload the payslip PDF file.',
        }

    def __init__(self, *args, **kwargs):
        self.startup = kwargs.pop('startup', None)
        super().__init__(*args, **kwargs)
        
        # Add form-control class to all fields
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs.update({
                    'class': 'form-control'
                })
        
        # Filter payroll queryset by startup and only paid payrolls
        if self.startup:
            self.fields['payroll'].queryset = Payroll.objects.filter(
                employee__startup=self.startup,
                paid=True
            ).select_related('employee', 'employee__user')
        else:
            self.fields['payroll'].queryset = Payroll.objects.none()
        
        # Make fields required
        self.fields['payroll'].required = True
        self.fields['pdf'].required = True


# forms.py - Exit Management Forms

class ExitRequestForm(forms.ModelForm):
    
    class Meta:
        model = ExitRequest
        fields = [
            'employee',
            'resignation_date',
            'last_working_day',
            'reason',
            'reason_description',
            'status',
            'exit_interview_date',
            'exit_interview_notes',
            'is_eligible_for_rehire',
            'feedback'
        ]
        widgets = {
            'employee': forms.Select(attrs={
                'class': 'form-control'
            }),
            'resignation_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'last_working_day': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'reason': forms.Select(attrs={
                'class': 'form-control'
            }),
            'reason_description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Please provide detailed reason...'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'exit_interview_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'exit_interview_notes': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Exit interview notes...'
            }),
            'is_eligible_for_rehire': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'feedback': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Employee feedback...'
            }),
        }
        labels = {
            'employee': 'Employee',
            'resignation_date': 'Resignation Date',
            'last_working_day': 'Last Working Day',
            'reason': 'Exit Reason',
            'reason_description': 'Reason Description',
            'status': 'Status',
            'exit_interview_date': 'Exit Interview Date',
            'exit_interview_notes': 'Exit Interview Notes',
            'is_eligible_for_rehire': 'Eligible for Rehire',
            'feedback': 'Employee Feedback',
        }
        help_texts = {
            'resignation_date': 'Date when the employee submitted resignation.',
            'last_working_day': 'Last working day of the employee.',
            'reason': 'Primary reason for leaving.',
            'is_eligible_for_rehire': 'Check if the employee can be rehired in the future.',
        }

    def __init__(self, *args, **kwargs):
        self.startup = kwargs.pop('startup', None)
        super().__init__(*args, **kwargs)
        
        # Add form-control class to all fields
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs.update({
                    'class': 'form-control'
                })
        
        # Filter employees by startup
        if self.startup:
            self.fields['employee'].queryset = Employee.objects.filter(
                startup=self.startup,
                is_active=True
            ).select_related('user')
        
        # Make fields required
        self.fields['employee'].required = True
        self.fields['resignation_date'].required = True
        self.fields['last_working_day'].required = True
        self.fields['reason'].required = True
        
        # Set status choices
        status_choices = [
            ('Pending', '⏳ Pending Approval'),
            ('Approved', '✅ Approved'),
            ('Rejected', '❌ Rejected'),
            ('Completed', '📋 Completed'),
            ('Cancelled', '🔄 Cancelled'),
        ]
        self.fields['status'].choices = status_choices

    def clean(self):
        cleaned_data = super().clean()
        resignation_date = cleaned_data.get('resignation_date')
        last_working_day = cleaned_data.get('last_working_day')
        
        if resignation_date and last_working_day:
            if resignation_date > last_working_day:
                raise ValidationError({
                    'last_working_day': 'Last working day must be after resignation date.'
                })
            
            from django.utils import timezone
            if resignation_date < timezone.now().date():
                raise ValidationError({
                    'resignation_date': 'Resignation date cannot be in the past.'
                })
        
        return cleaned_data


class ExitFilterForm(forms.Form):
    """Form for filtering exit requests"""
    
    def __init__(self, *args, startup=None, **kwargs):
        super().__init__(*args, **kwargs)
        if startup:
            self.fields['employee'].queryset = Employee.objects.filter(
                startup=startup,
                is_active=True
            ).select_related('user')
    
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.none(),
        required=False,
        empty_label='All Employees',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=[
            ('', 'All Status'),
            ('Pending', '⏳ Pending'),
            ('Approved', '✅ Approved'),
            ('Rejected', '❌ Rejected'),
            ('Completed', '📋 Completed'),
            ('Cancelled', '🔄 Cancelled'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    reason = forms.ChoiceField(
        choices=[
            ('', 'All Reasons'),
            ('better_opportunity', 'Better Opportunity'),
            ('career_growth', 'Career Growth'),
            ('salary', 'Salary/Package'),
            ('relocation', 'Relocation'),
            ('personal', 'Personal Reasons'),
            ('health', 'Health Issues'),
            ('retirement', 'Retirement'),
            ('other', 'Other'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    from_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='From Date'
    )
    to_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='To Date'
    )


# forms.py - Performance Review Forms

class PerformanceReviewForm(forms.ModelForm):
    
    class Meta:
        model = PerformanceReview
        fields = [
            'employee',
            'reviewer',
            'rating',
            'review',
            'strengths',
            'areas_for_improvement',
            'goals',
            'review_period'
        ]
        widgets = {
            'employee': forms.Select(attrs={
                'class': 'form-control'
            }),
            'reviewer': forms.Select(attrs={
                'class': 'form-control'
            }),
            'rating': forms.Select(attrs={
                'class': 'form-control'
            }),
            'review': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-control',
                'placeholder': 'Detailed performance review...'
            }),
            'strengths': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Key strengths of the employee...'
            }),
            'areas_for_improvement': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Areas for improvement...'
            }),
            'goals': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Goals for next period...'
            }),
            'review_period': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'employee': 'Employee',
            'reviewer': 'Reviewer',
            'rating': 'Rating',
            'review': 'Review',
            'strengths': 'Strengths',
            'areas_for_improvement': 'Areas for Improvement',
            'goals': 'Goals',
            'review_period': 'Review Period',
        }
        help_texts = {
            'review': 'Provide a detailed performance review.',
            'strengths': 'List the key strengths of the employee.',
            'areas_for_improvement': 'Identify areas where the employee can improve.',
            'goals': 'Set goals for the next review period.',
        }

    def __init__(self, *args, **kwargs):
        self.startup = kwargs.pop('startup', None)
        super().__init__(*args, **kwargs)
        
        # Add form-control class to all fields
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs.update({
                    'class': 'form-control'
                })
        
        # Filter employees by startup
        if self.startup:
            self.fields['employee'].queryset = Employee.objects.filter(
                startup=self.startup,
                is_active=True
            ).select_related('user')
        
        # Set reviewer choices
        self.fields['reviewer'].queryset = User.objects.filter(
            is_active=True
        ).exclude(id=1)  # Exclude superuser if needed
        
        # Make fields required
        self.fields['employee'].required = True
        self.fields['reviewer'].required = True
        self.fields['rating'].required = True
        self.fields['review'].required = True
        
        # Set rating choices with stars
        rating_choices = [
            (1, '⭐ 1 - Poor'),
            (2, '⭐⭐ 2 - Below Average'),
            (3, '⭐⭐⭐ 3 - Average'),
            (4, '⭐⭐⭐⭐ 4 - Good'),
            (5, '⭐⭐⭐⭐⭐ 5 - Excellent'),
        ]
        self.fields['rating'].choices = rating_choices


class PerformanceFilterForm(forms.Form):
    """Form for filtering performance reviews"""
    
    def __init__(self, *args, startup=None, **kwargs):
        super().__init__(*args, **kwargs)
        if startup:
            self.fields['employee'].queryset = Employee.objects.filter(
                startup=startup,
                is_active=True
            ).select_related('user')
    
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.none(),
        required=False,
        empty_label='All Employees',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    rating = forms.ChoiceField(
        choices=[
            ('', 'All Ratings'),
            ('5', '⭐⭐⭐⭐⭐ 5 - Excellent'),
            ('4', '⭐⭐⭐⭐ 4 - Good'),
            ('3', '⭐⭐⭐ 3 - Average'),
            ('2', '⭐⭐ 2 - Below Average'),
            ('1', '⭐ 1 - Poor'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    review_period = forms.ChoiceField(
        choices=[
            ('', 'All Periods'),
            ('quarterly', 'Quarterly'),
            ('half_yearly', 'Half Yearly'),
            ('annual', 'Annual'),
            ('project_based', 'Project Based'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    from_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='From Date'
    )
    to_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='To Date'
    )



# people/forms.py - Add this custom form

class EmployeeLeaveRequestForm(forms.ModelForm):
    """Form for employees to create leave requests (without employee/status fields)"""
    
    class Meta:
        model = LeaveRequest
        exclude = ['employee', 'status', 'approved_by']
        widgets = {
            'leave_type': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select leave type'
            }),
            'from_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'to_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Please provide a reason for your leave request...'
            }),
        }


# people/forms.py - Add these forms

class EmployeeTimingConfigForm(forms.ModelForm):
    """Form for configuring employee attendance timings"""
    
    class Meta:
        model = Employee
        fields = [
            'default_check_in', 'default_check_out',
            'work_start_time', 'work_end_time',
            'grace_period_minutes', 'half_day_hours', 'full_day_hours',
            'overtime_enabled', 'overtime_rate', 'shift'
        ]
        widgets = {
            'default_check_in': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'default_check_out': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'work_start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'work_end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'grace_period_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 60}),
            'half_day_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': 0}),
            'full_day_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': 0}),
            'overtime_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'overtime_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': 1}),
            'shift': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values if not set
        if not self.instance.pk:
            self.initial['grace_period_minutes'] = 15
            self.initial['half_day_hours'] = 4.00
            self.initial['full_day_hours'] = 8.00
            self.initial['overtime_enabled'] = False
            self.initial['overtime_rate'] = 1.5


# people/forms.py - Add this form

class DepartmentTimingConfigForm(forms.ModelForm):
    """Form for department timing configuration"""
    
    class Meta:
        model = DepartmentTimingConfig
        fields = [
            'work_start_time', 'work_end_time', 'grace_period_minutes',
            'half_day_hours', 'full_day_hours', 'shift', 'weekly_off_days'
        ]
        widgets = {
            'work_start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'work_end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'grace_period_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 60}),
            'half_day_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': 0}),
            'full_day_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': 0}),
            'shift': forms.Select(attrs={'class': 'form-control'}),
            'weekly_off_days': forms.SelectMultiple(attrs={'class': 'form-control'}, choices=[
                ('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'),
                ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')
            ]),
        }