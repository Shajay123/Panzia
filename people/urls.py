# people/urls.py - Complete updated file

from django.urls import path
from . import views

urlpatterns = [

    # ============================================================
    # DASHBOARD
    # ============================================================
    
    path("", views.people_dashboard, name="people_dashboard"),

    # ============================================================
    # EMPLOYEE MANAGEMENT
    # ============================================================
    
    path("employees/", views.employees, name="employees"),
    path("employees/add/", views.employee_create, name="employee_create"),
    path("employees/<int:id>/", views.employee_detail, name="employee_detail"),
    path("employees/<int:id>/edit/", views.employee_update, name="employee_update"),
    path("employees/<int:id>/delete/", views.employee_delete, name="employee_delete"),

    # ============================================================
    # DEPARTMENTS
    # ============================================================
    
    path("departments/", views.departments, name="departments"),
    path("departments/create/", views.department_create, name="department_create"),
    path("departments/<int:id>/", views.department_detail, name="department_detail"),
    path("departments/<int:id>/update/", views.department_update, name="department_update"),
    path("departments/<int:id>/delete/", views.department_delete, name="department_delete"),

    # ============================================================
    # ATTENDANCE (HR/Admin)
    # ============================================================
    
    path("attendance/", views.attendance, name="attendance"),
    path("attendance/create/", views.attendance_create, name="attendance_create"),
    path("attendance/<int:id>/", views.attendance_detail, name="attendance_detail"),
    path("attendance/<int:id>/edit/", views.attendance_update, name="attendance_update"),
    path("attendance/<int:id>/delete/", views.attendance_delete, name="attendance_delete"),
    path("attendance/report/", views.attendance_report, name="attendance_report"),

    # ============================================================
    # LEAVE MANAGEMENT (HR/Admin)
    # ============================================================
    
    path("leave/", views.leave_dashboard, name="leave_dashboard"),
    path("leave/requests/", views.leave_requests, name="leave_requests"),
    path("leave/create/", views.leave_create, name="leave_create"),
    path("leave/<int:id>/", views.leave_detail, name="leave_detail"),
    path("leave/<int:id>/edit/", views.leave_update, name="leave_update"),
    path("leave/<int:id>/approve/", views.leave_approve, name="leave_approve"),
    path("leave/<int:id>/reject/", views.leave_reject, name="leave_reject"),
    path("leave/<int:id>/delete/", views.leave_delete, name="leave_delete"),

    # ============================================================
    # PAYROLL (HR/Admin)
    # ============================================================
    
    path("payroll/", views.payroll, name="payroll"),
    path("payroll/create/", views.payroll_create, name="payroll_create"),
    path("payroll/<int:id>/", views.payroll_detail, name="payroll_detail"),
    path("payroll/<int:id>/edit/", views.payroll_update, name="payroll_update"),
    path("payroll/<int:id>/mark-paid/", views.payroll_mark_paid, name="payroll_mark_paid"),
    path("payroll/<int:id>/delete/", views.payroll_delete, name="payroll_delete"),

    # ============================================================
    # PAYSLIPS (HR/Admin Only - Employees don't get payslips directly)
    # ============================================================
    
    path("payslips/", views.payslips, name="payslips"),
    path("payslips/create/", views.payslip_create, name="payslip_create"),
    path("payslips/<int:id>/", views.payslip_detail, name="payslip_detail"),
    path("payslips/<int:id>/edit/", views.payslip_update, name="payslip_update"),
    path("payslips/<int:id>/delete/", views.payslip_delete, name="payslip_delete"),
    path("payslips/<int:id>/preview/", views.payslip_preview, name="payslip_preview"),
    path("payslips/<int:id>/regenerate/", views.payslip_regenerate, name="payslip_regenerate"),
    path("payslips/<int:id>/download/", views.payslip_download_pdf, name="payslip_download_pdf"),
    path("payslips/bulk-generate/", views.payslip_bulk_generate, name="payslip_bulk_generate"),

    # ============================================================
    # PERFORMANCE REVIEWS
    # ============================================================
    
    path("performance/", views.performance, name="performance"),
    path("performance/create/", views.performance_create, name="performance_create"),
    path("performance/<int:id>/", views.performance_detail, name="performance_detail"),
    path("performance/<int:id>/edit/", views.performance_update, name="performance_update"),
    path("performance/<int:id>/delete/", views.performance_delete, name="performance_delete"),

    # ============================================================
    # EMPLOYEE DOCUMENTS
    # ============================================================
    
    path("documents/", views.documents, name="documents"),
    path("documents/upload/", views.document_create, name="document_create"),
    path("documents/<int:id>/", views.document_detail, name="document_detail"),
    path("documents/<int:id>/edit/", views.document_update, name="document_update"),
    path("documents/<int:id>/delete/", views.document_delete, name="document_delete"),

    # ============================================================
    # ONBOARDING
    # ============================================================
    
    path("onboarding/", views.onboarding, name="onboarding"),

    # ============================================================
    # EXIT MANAGEMENT
    # ============================================================
    
    path("exit/", views.exit_management, name="exit_management"),
    path("exit/create/", views.exit_create, name="exit_create"),
    path("exit/<int:id>/", views.exit_detail, name="exit_detail"),
    path("exit/<int:id>/edit/", views.exit_update, name="exit_update"),
    path("exit/<int:id>/approve/", views.exit_approve, name="exit_approve"),
    path("exit/<int:id>/reject/", views.exit_reject, name="exit_reject"),
    path("exit/<int:id>/complete/", views.exit_complete, name="exit_complete"),
    path("exit/<int:id>/delete/", views.exit_delete, name="exit_delete"),

    # ============================================================
    # HOLIDAYS
    # ============================================================
    
    path("holidays/", views.holidays, name="holidays"),
    path("holidays/create/", views.holiday_create, name="holiday_create"),
    path("holidays/<int:id>/", views.holiday_detail, name="holiday_detail"),
    path("holidays/<int:id>/edit/", views.holiday_update, name="holiday_update"),
    path("holidays/<int:id>/delete/", views.holiday_delete, name="holiday_delete"),

    # ============================================================
    # SUPER ADMIN STARTUP SWITCHING
    # ============================================================
    
    path("switch-startup/<int:startup_id>/", views.switch_startup, name="switch_startup"),
    path("reset-startup-view/", views.reset_startup_view, name="reset_startup_view"),
    path("api/startups/", views.get_startup_list, name="api_startup_list"),

    # ============================================================
    # EMPLOYEE PORTAL (Self-Service)
    # ============================================================

    # ---- Dashboard ----
    path("employee/", views.employee_portal_dashboard, name="employee_portal_dashboard"),

    # ---- Profile ----
    path("employee/profile/", views.employee_portal_profile, name="employee_portal_profile"),

    # ---- Attendance ----
    # Calendar View
    path("employee/attendance/", views.employee_portal_attendance, name="employee_portal_attendance"),
    
    # Check-in / Check-out (Quick Actions)
    path("employee/attendance/checkin/", views.employee_portal_attendance_checkin, name="employee_portal_attendance_checkin"),
    path("employee/attendance/checkout/", views.employee_portal_attendance_checkout, name="employee_portal_attendance_checkout"),
    
    # API URLs for AJAX
    path("api/attendance/checkin/", views.employee_attendance_checkin_api, name="employee_attendance_checkin_api"),
    path("api/attendance/checkout/", views.employee_attendance_checkout_api, name="employee_attendance_checkout_api"),
    
    # Photo Upload
    path("employee/attendance/upload-photo/", views.attendance_upload_photo, name="attendance_upload_photo"),

    # ---- Leave ----
    path("employee/leave/", views.employee_portal_leave, name="employee_portal_leave"),
    path("employee/leave/create/", views.employee_portal_leave_create, name="employee_portal_leave_create"),
    path("employee/leave/<int:id>/", views.employee_portal_leave_detail, name="employee_portal_leave_detail"),

    # ---- Payroll ----
    path("employee/payroll/", views.employee_portal_payroll, name="employee_portal_payroll"),

    # ============================================================
    # EMPLOYEE PAYSLIPS - REMOVED
    # Employees don't get payslips directly - only HR/Admin
    # ============================================================
    # path("employee/payslips/", views.employee_portal_payslips, name="employee_portal_payslips"),

    # ============================================================
    # TIMING CONFIGURATION (HR/Admin)
    # ============================================================
    
    path("employee/<int:employee_id>/timing/", views.employee_timing_config, name="employee_timing_config"),
    path("department/<int:department_id>/timing/", views.department_timing_config, name="department_timing_config"),
    path("api/employee/<int:employee_id>/timing/", views.get_employee_timing, name="api_employee_timing"),
]