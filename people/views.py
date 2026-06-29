
from django.utils import timezone
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from accounts.models import User
from people.forms import EmployeeForm
from startups.models import StartupProfile

from .models import (
    Employee,
    Department,
    Attendance,
    Holiday,
    LeaveRequest,
    Payroll,
    Payslip,
    PerformanceReview,
    EmployeeDocument
)


@login_required
def people_dashboard(request):

    startup = StartupProfile.objects.get(
        user=request.user
    )

    from datetime import date
    today = date.today()

    recent_employees = Employee.objects.filter(
        startup=startup
    ).order_by("-created_at")[:5]

    present_today = Attendance.objects.filter(
        employee__startup=startup,
        date=today,
        status="Present"
    ).count()

    absent_today = Attendance.objects.filter(
        employee__startup=startup,
        date=today,
        status="Absent"
    ).count()

    wfh_today = Attendance.objects.filter(
        employee__startup=startup,
        date=today,
        status="WFH"
    ).count()

    leave_today = Attendance.objects.filter(
        employee__startup=startup,
        date=today,
        status="Leave"
    ).count()

    context = {

        "employee_count": Employee.objects.filter(
            startup=startup
        ).count(),

        "department_count": Department.objects.count(),

        "attendance_count": Attendance.objects.filter(
            employee__startup=startup
        ).count(),

        "leave_count": LeaveRequest.objects.filter(
            employee__startup=startup
        ).count(),

        "payroll_count": Payroll.objects.filter(
            employee__startup=startup
        ).count(),

        "recent_employees": recent_employees,

        "present_today": present_today,

        "absent_today": absent_today,

        "wfh_today": wfh_today,

        "leave_today": leave_today,

    }

    return render(
        request,
        "people/dashboard.html",
        context
    )


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.models import User
from startups.models import StartupProfile

from .models import (
    Employee,
    Department,
    Attendance,
    LeaveRequest,
)

from .forms import AttendanceForm, DepartmentForm, EmployeeDocumentForm, EmployeeForm


# ============================================================
# Helper
# ============================================================

def get_startup(request):
    return get_object_or_404(
        StartupProfile,
        user=request.user
    )


# ============================================================
# CREATE EMPLOYEE
# ============================================================

@login_required
def employee_create(request):

    startup = get_startup(request)

    if request.method == "POST":

        form = EmployeeForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            employee = form.save(commit=False)

            employee.startup = startup

            hire_mode = request.POST.get("hire_mode")

            # ----------------------------------------
            # Talent Pool
            # ----------------------------------------

            if hire_mode == "talent":

                user = get_object_or_404(
                    User,
                    id=request.POST.get("talent_user"),
                    role="talent"
                )

            # ----------------------------------------
            # Existing User
            # ----------------------------------------

            elif hire_mode == "existing":

                user = get_object_or_404(
                    User,
                    id=request.POST.get("existing_user")
                )

            # ----------------------------------------
            # Brand New Employee
            # ----------------------------------------

            else:

                username = request.POST.get("username")
                email = request.POST.get("email")
                first_name = request.POST.get("first_name")
                last_name = request.POST.get("last_name")

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password="ChangeMe@123",
                    role="employee"
                )

            employee.user = user

            employee.save()

            messages.success(
                request,
                "Employee added successfully."
            )

            return redirect("employees")

    else:

        form = EmployeeForm()

    talent_users = User.objects.filter(
        role="talent"
    ).exclude(
        employee__isnull=False
    )

    existing_users = User.objects.filter(
        employee__isnull=True
    ).exclude(
        role="talent"
    ).exclude(
        id=request.user.id
    )

    departments = Department.objects.filter(
        startup=startup
    )

    return render(
        request,
        "people/employee_create.html",
        {
            "form": form,
            "talent_users": talent_users,
            "existing_users": existing_users,
            "departments": departments,
        },
    )


# ============================================================
# EMPLOYEE DETAIL
# ============================================================

@login_required
def employee_detail(request, id):

    startup = get_startup(request)

    employee = get_object_or_404(
        Employee,
        id=id,
        startup=startup
    )

    attendance_count = Attendance.objects.filter(
        employee=employee
    ).count()

    leave_count = LeaveRequest.objects.filter(
        employee=employee
    ).count()

    return render(
        request,
        "people/employee_detail.html",
        {
            "employee": employee,
            "attendance_count": attendance_count,
            "leave_count": leave_count,
        },
    )


# ============================================================
# EMPLOYEE LIST
# ============================================================

@login_required
def employees(request):

    startup = get_startup(request)

    employees = Employee.objects.filter(
        startup=startup
    ).select_related(
        "user",
        "department",
        "manager",
    ).order_by(
        "user__first_name",
        "user__last_name"
    )

    departments = Department.objects.filter(
    startup=startup
)

    return render(
        request,
        "people/employees.html",
        {
            "employees": employees,
            "departments": departments,
        },
    )


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Employee, Department
from .forms import EmployeeForm


@login_required
def employee_update(request, id):

    startup = get_startup(request)

    employee = get_object_or_404(
        Employee,
        id=id,
        startup=startup
    )

    if request.method == "POST":

        form = EmployeeForm(
            request.POST,
            request.FILES,
            instance=employee
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Employee updated successfully."
            )

            return redirect(
                "employee_detail",
                id=employee.id
            )

    else:

        form = EmployeeForm(
            instance=employee
        )

    return render(
        request,
        "people/employee_update.html",
        {
            "form": form,
            "employee": employee,
        }
    )


@login_required
def employee_delete(request, id):

    startup = get_startup(request)

    employee = get_object_or_404(
        Employee,
        id=id,
        startup=startup
    )

    if request.method == "POST":

        employee.delete()

        messages.success(
            request,
            "Employee deleted successfully."
        )

        return redirect("employees")

    return render(
        request,
        "people/employee_delete.html",
        {
            "employee": employee,
        }
    )
# ============================================================
# DEPARTMENTS
# ============================================================

@login_required
def departments(request):

    startup = get_startup(request)

    departments = Department.objects.filter(
        startup=startup
    ).prefetch_related(
        "employee_set"
    )

    return render(
        request,
        "people/departments.html",
        {
            "departments": departments,
        },
    )


from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .models import Department, Employee
from .forms import DepartmentForm


@login_required
def department_create(request):

    startup = get_startup(request)

    if request.method == "POST":

        form = DepartmentForm(request.POST)

        if form.is_valid():

            department = form.save(commit=False)

            department.startup = startup

            department.save()

            messages.success(
                request,
                "Department created successfully."
            )

            return redirect("departments")

    else:

        form = DepartmentForm()

    return render(
        request,
        "people/department_create.html",
        {
            "form": form
        }
    )


@login_required
def department_detail(request, id):

    startup = get_startup(request)

    department = get_object_or_404(
        Department,
        id=id,
        startup=startup
    )

    employees = Employee.objects.filter(
        department=department
    )

    return render(
        request,
        "people/department_detail.html",
        {
            "department": department,
            "employees": employees
        }
    )


@login_required
def department_update(request, id):

    startup = get_startup(request)

    department = get_object_or_404(
        Department,
        id=id,
        startup=startup
    )

    if request.method == "POST":

        form = DepartmentForm(
            request.POST,
            instance=department
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Department updated successfully."
            )

            return redirect(
                "department_detail",
                id=department.id
            )

    else:

        form = DepartmentForm(instance=department)

    return render(
        request,
        "people/department_update.html",
        {
            "form": form,
            "department": department
        }
    )


@login_required
def department_delete(request, id):

    startup = get_startup(request)

    department = get_object_or_404(
        Department,
        id=id,
        startup=startup
    )

    if request.method == "POST":

        department.delete()

        messages.success(
            request,
            "Department deleted successfully."
        )

        return redirect("departments")

    return render(
        request,
        "people/department_delete.html",
        {
            "department": department
        }
    )


@login_required
def attendance(request):

    startup = get_startup(request)

    records = Attendance.objects.select_related(
        "employee",
        "employee__user"
    ).filter(
        employee__startup=startup
    ).order_by("-date")

    today = timezone.now().date()

    context = {

        "attendance": records,

        "total": records.filter(date=today).count(),

        "present": records.filter(
            date=today,
            status="Present"
        ).count(),

        "absent": records.filter(
            date=today,
            status="Absent"
        ).count(),

        "leave": records.filter(
            date=today,
            status="Leave"
        ).count(),

        "wfh": records.filter(
            date=today,
            status="WFH"
        ).count(),

    }

    return render(
        request,
        "people/attendance.html",
        context
    )


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db import IntegrityError

@login_required
def attendance_create(request):

    startup = get_startup(request)

    employees = Employee.objects.filter(
        startup=startup
    ).select_related("user")

    if request.method == "POST":

        form = AttendanceForm(request.POST)

        form.fields["employee"].queryset = employees

        if form.is_valid():

            employee = form.cleaned_data["employee"]
            date = form.cleaned_data["date"]

            # Prevent duplicate attendance
            if Attendance.objects.filter(
                employee=employee,
                date=date
            ).exists():

                messages.error(
                    request,
                    f"Attendance has already been marked for {employee.user.get_full_name()} on {date}."
                )

            else:

                try:

                    form.save()

                    messages.success(
                        request,
                        "Attendance marked successfully."
                    )

                    return redirect("attendance")

                except IntegrityError:

                    messages.error(
                        request,
                        "Attendance already exists for this employee."
                    )

    else:

        form = AttendanceForm()

        form.fields["employee"].queryset = employees

    return render(
        request,
        "people/attendance_create.html",
        {
            "form": form
        }
    )

@login_required
def attendance_detail(request, id):

    startup = get_startup(request)

    attendance  = get_object_or_404(
        Attendance,
        id=id,
        employee__startup=startup
    )

    return render(
        request,
        "people/attendance_detail.html",
        {
            "attendance": attendance 
        }
    )

@login_required
def attendance_update(request, id):

    startup = get_startup(request)

    attendance = get_object_or_404(
        Attendance,
        id=id,
        employee__startup=startup
    )

    if request.method == "POST":

        form = AttendanceForm(
            request.POST,
            instance=attendance
        )

        form.fields["employee"].queryset = Employee.objects.filter(
            startup=startup
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Attendance updated."
            )

            return redirect(
                "attendance_detail",
                id=attendance.id
            )

    else:

        form = AttendanceForm(
            instance=attendance
        )

        form.fields["employee"].queryset = Employee.objects.filter(
            startup=startup
        )

    return render(
        request,
        "people/attendance_update.html",
        {
            "form": form,
            "attendance": attendance
        }
    )

@login_required
def attendance_delete(request, id):

    startup = get_startup(request)

    attendance = get_object_or_404(
        Attendance,
        id=id,
        employee__startup=startup
    )

    if request.method == "POST":

        attendance.delete()

        messages.success(
            request,
            "Attendance deleted."
        )

        return redirect("attendance")

    return render(
        request,
        "people/attendance_delete.html",
        {
            "attendance": attendance
        }
    )

@login_required
def attendance_report(request):

    startup = get_startup(request)

    records = Attendance.objects.select_related(
        "employee",
        "employee__user"
    ).filter(
        employee__startup=startup
    ).order_by("-date")

    employees = Employee.objects.filter(
        startup=startup
    ).select_related("user")

    employee = request.GET.get("employee")
    status = request.GET.get("status")
    from_date = request.GET.get("from")
    to_date = request.GET.get("to")

    if employee:
        records = records.filter(employee_id=employee)

    if status:
        records = records.filter(status=status)

    if from_date:
        records = records.filter(date__gte=from_date)

    if to_date:
        records = records.filter(date__lte=to_date)

    present = records.filter(status="Present").count()
    absent = records.filter(status="Absent").count()
    leave = records.filter(status="Leave").count()
    wfh = records.filter(status="WFH").count()

    total = records.count()

    attendance_percentage = round(
        (present / total) * 100,
        2
    ) if total else 0

    context = {

        "records": records,

        "employees": employees,

        "present_count": present,

        "absent_count": absent,

        "leave_count": leave,

        "wfh_count": wfh,

        "attendance_percentage": attendance_percentage,

    }

    return render(
        request,
        "people/attendance_report.html",
        context,
    )


@login_required
def leave_dashboard(request):

    pending = LeaveRequest.objects.filter(
        status="Pending"
    ).count()

    approved = LeaveRequest.objects.filter(
        status="Approved"
    ).count()

    rejected = LeaveRequest.objects.filter(
        status="Rejected"
    ).count()

    context = {

        "pending": pending,
        "approved": approved,
        "rejected": rejected

    }

    return render(
        request,
        "people/leave_dashboard.html",
        context
    )


@login_required
def leave_requests(request):

    requests = LeaveRequest.objects.select_related(
        "employee"
    )

    return render(
        request,
        "people/leave_requests.html",
        {
            "requests": requests
        }
    )

@login_required
def payroll(request):

    payrolls = Payroll.objects.select_related(
        "employee"
    )

    return render(
        request,
        "people/payroll.html",
        {
            "payrolls": payrolls
        }
    )


@login_required
def performance(request):

    reviews = PerformanceReview.objects.select_related(
        "employee"
    )

    return render(
        request,
        "people/performance.html",
        {
            "reviews": reviews
        }
    )


@login_required
def documents(request):

    startup = get_startup(request)

    docs = (
        EmployeeDocument.objects
        .select_related(
            "employee",
            "employee__user",
            "employee__department"
        )
        .filter(employee__startup=startup)
        .order_by("-uploaded_at")
    )

    context = {

        "documents": docs,

        "total_documents": docs.count(),

        "verified_documents": docs.count(),

        "pending_documents": 0,

        "employees_count": Employee.objects.filter(
            startup=startup
        ).count(),

    }

    return render(
        request,
        "people/documents.html",
        context
    )


@login_required
def document_create(request):

    startup = get_startup(request)

    if request.method == "POST":

        form = EmployeeDocumentForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            doc = form.save(commit=False)

            if doc.employee.startup != startup:

                messages.error(
                    request,
                    "Invalid employee selected."
                )

                return redirect("documents")

            doc.save()

            messages.success(
                request,
                "Document uploaded successfully."
            )

            return redirect("documents")

    else:

        form = EmployeeDocumentForm()

        form.fields["employee"].queryset = Employee.objects.filter(
            startup=startup
        )

    return render(
        request,
        "people/document_create.html",
        {
            "form": form
        }
    )


@login_required
def document_detail(request, id):

    startup = get_startup(request)

    document = get_object_or_404(
        EmployeeDocument,
        id=id,
        employee__startup=startup
    )

    return render(
        request,
        "people/document_detail.html",
        {
            "document": document
        }
    )

@login_required
def document_update(request, id):

    startup = get_startup(request)

    document = get_object_or_404(
        EmployeeDocument,
        id=id,
        employee__startup=startup
    )

    if request.method == "POST":

        form = EmployeeDocumentForm(
            request.POST,
            request.FILES,
            instance=document
        )

        form.fields["employee"].queryset = Employee.objects.filter(
            startup=startup
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Document updated successfully."
            )

            return redirect(
                "document_detail",
                id=document.id
            )

    else:

        form = EmployeeDocumentForm(instance=document)

        form.fields["employee"].queryset = Employee.objects.filter(
            startup=startup
        )

    return render(
        request,
        "people/document_update.html",
        {
            "form": form,
            "document": document
        }
    )

@login_required
def document_delete(request, id):

    startup = get_startup(request)

    document = get_object_or_404(
        EmployeeDocument,
        id=id,
        employee__startup=startup
    )

    if request.method == "POST":

        document.delete()

        messages.success(
            request,
            "Document deleted successfully."
        )

        return redirect("documents")

    return render(
        request,
        "people/document_delete.html",
        {
            "document": document
        }
    )

@login_required
def onboarding(request):

    employees = Employee.objects.filter(
        startup__user=request.user
    )

    return render(
        request,
        "people/onboarding.html",
        {
            "employees": employees
        }
    )


@login_required
def exit_management(request):

    exited_employees = []

    return render(
        request,
        "people/exit_management.html",
        {
            "exited_employees": exited_employees
        }
    )


@login_required
def holidays(request):

    holiday_list = Holiday.objects.all().order_by(
        "date"
    )

    return render(
        request,
        "people/holidays.html",
        {
            "holidays": holiday_list
        }
    )


@login_required
def payslips(request):

    payslips = Payslip.objects.select_related(
        "payroll",
        "payroll__employee"
    )

    return render(
        request,
        "people/payslips.html",
        {
            "payslips": payslips
        }
    )