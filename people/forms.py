from django import forms

from .models import (
    Employee,
    Department,
    Attendance,
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
            "is_active",

            "profile_image",

            "notes",

        ]

        widgets = {

            "joining_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "probation_end": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "confirmation_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Additional notes about this employee..."
                }
            ),

        }

    def __init__(self, *args, startup=None, **kwargs):

        super().__init__(*args, **kwargs)

        # Bootstrap styling

        for name, field in self.fields.items():

            if isinstance(field.widget, forms.CheckboxInput):

                field.widget.attrs.update({
                    "class": "form-check-input"
                })

            elif isinstance(field.widget, forms.Textarea):

                field.widget.attrs.update({
                    "class": "form-control"
                })

            else:

                field.widget.attrs.update({
                    "class": "form-control"
                })

        # Department only for this startup

        if startup:

            self.fields["department"].queryset = Department.objects.filter(
                startup=startup
            )

            self.fields["manager"].queryset = Employee.objects.filter(
                startup=startup
            )

        # Nice placeholders

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

class AttendanceForm(forms.ModelForm):

    class Meta:

        model = Attendance

        fields = "__all__"

        widgets = {

            "date": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),

            "check_in": forms.TimeInput(
                attrs={
                    "type": "time"
                }
            ),

            "check_out": forms.TimeInput(
                attrs={
                    "type": "time"
                }
            ),

            "notes": forms.Textarea(
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
# LEAVE REQUEST
# =====================================================

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
            )

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field in self.fields.values():

            field.widget.attrs.update({
                "class": "form-control"
            })


# =====================================================
# PAYROLL
# =====================================================

class PayrollForm(forms.ModelForm):

    class Meta:

        model = Payroll

        fields = "__all__"

        widgets = {

            "paid_date": forms.DateInput(
                attrs={
                    "type": "date"
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
# PERFORMANCE
# =====================================================

class PerformanceReviewForm(forms.ModelForm):

    class Meta:

        model = PerformanceReview

        fields = "__all__"

        widgets = {

            "review": forms.Textarea(
                attrs={
                    "rows": 5
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


# =====================================================
# HOLIDAY
# =====================================================

class HolidayForm(forms.ModelForm):

    class Meta:

        model = Holiday

        fields = "__all__"

        widgets = {

            "date": forms.DateInput(
                attrs={
                    "type": "date"
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
# PAYSLIP
# =====================================================

class PayslipForm(forms.ModelForm):

    class Meta:

        model = Payslip

        fields = "__all__"

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field in self.fields.values():

            field.widget.attrs.update({
                "class": "form-control"
            })