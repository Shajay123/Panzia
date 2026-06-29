from django.urls import path
from . import views

urlpatterns = [

    # Dashboard
    path("", views.people_dashboard, name="people_dashboard"),

    # Employees
    path("employees/", views.employees, name="employees"),
    path("employees/add/", views.employee_create, name="employee_create"),
    path("employees/<int:id>/", views.employee_detail, name="employee_detail"),
    path(
        "employees/<int:id>/edit/",
        views.employee_update,
        name="employee_update"
    ),

    path(
        "employees/<int:id>/delete/",
        views.employee_delete,
        name="employee_delete"
    ),

    # Departments
    path("departments/", views.departments, name="departments"),

    path(
        "departments/create/",
        views.department_create,
        name="department_create"
    ),

    path(
        "departments/<int:id>/",
        views.department_detail,
        name="department_detail"
    ),

    path(
        "departments/<int:id>/update/",
        views.department_update,
        name="department_update"
    ),

    path(
        "departments/<int:id>/delete/",
        views.department_delete,
        name="department_delete"
    ),

   
    # Attendance
path("attendance/", views.attendance, name="attendance"),

path(
    "attendance/create/",
    views.attendance_create,
    name="attendance_create"
),

path(
    "attendance/<int:id>/",
    views.attendance_detail,
    name="attendance_detail"
),

path(
    "attendance/<int:id>/edit/",
    views.attendance_update,
    name="attendance_update"
),

path(
    "attendance/<int:id>/delete/",
    views.attendance_delete,
    name="attendance_delete"
),

path(
    "attendance/report/",
    views.attendance_report,
    name="attendance_report"
),

    # Leave
    path("leave/", views.leave_dashboard, name="leave_dashboard"),
    path("leave/requests/", views.leave_requests, name="leave_requests"),

    # Payroll
    path("payroll/", views.payroll, name="payroll"),
    path("payslips/", views.payslips, name="payslips"),

    # Performance
    path("performance/", views.performance, name="performance"),

    # Employee Documents
path(
    "documents/",
    views.documents,
    name="documents"
),

path(
    "documents/upload/",
    views.document_create,
    name="document_create"
),

path(
    "documents/<int:id>/",
    views.document_detail,
    name="document_detail"
),

path(
    "documents/<int:id>/edit/",
    views.document_update,
    name="document_update"
),

path(
    "documents/<int:id>/delete/",
    views.document_delete,
    name="document_delete"
),
   

    


    # Onboarding
    path("onboarding/", views.onboarding, name="onboarding"),

    # Exit
    path("exit/", views.exit_management, name="exit_management"),

    # Holidays
    path("holidays/", views.holidays, name="holidays"),

]