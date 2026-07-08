from django.contrib import admin
from .models import (
    GSTFiling, TDSFiling, PFContribution, ESICContribution,
    MCAFiling, IncomeTaxFiling, ComplianceReminder
)

@admin.register(GSTFiling)
class GSTFilingAdmin(admin.ModelAdmin):
    list_display = ['startup', 'return_type', 'month', 'year', 'due_date', 'status', 'filed']
    list_filter = ['startup', 'return_type', 'status', 'filed', 'year']
    search_fields = ['startup__company_name', 'month', 'return_type']
    ordering = ['-due_date']
    readonly_fields = ['created_at']

@admin.register(TDSFiling)
class TDSFilingAdmin(admin.ModelAdmin):
    list_display = ['startup', 'quarter', 'year', 'amount', 'due_date', 'status', 'filed']
    list_filter = ['startup', 'status', 'filed', 'year']
    search_fields = ['startup__company_name', 'quarter']
    ordering = ['-due_date']

@admin.register(PFContribution)
class PFContributionAdmin(admin.ModelAdmin):
    list_display = ['startup', 'month', 'employee_count', 'amount', 'due_date', 'paid']
    list_filter = ['startup', 'paid', 'month']
    search_fields = ['startup__company_name', 'month']
    ordering = ['-due_date']

@admin.register(ESICContribution)
class ESICContributionAdmin(admin.ModelAdmin):
    list_display = ['startup', 'month', 'amount', 'due_date', 'paid']
    list_filter = ['startup', 'paid', 'month']
    search_fields = ['startup__company_name', 'month']
    ordering = ['-due_date']

@admin.register(MCAFiling)
class MCAFilingAdmin(admin.ModelAdmin):
    list_display = ['startup', 'filing_name', 'due_date', 'status', 'filed']
    list_filter = ['startup', 'status', 'filed']
    search_fields = ['startup__company_name', 'filing_name']
    ordering = ['-due_date']

@admin.register(IncomeTaxFiling)
class IncomeTaxFilingAdmin(admin.ModelAdmin):
    list_display = ['startup', 'assessment_year', 'taxable_income', 'tax_amount', 'due_date', 'status', 'filed']
    list_filter = ['startup', 'status', 'filed']
    search_fields = ['startup__company_name', 'assessment_year']
    ordering = ['-due_date']

@admin.register(ComplianceReminder)
class ComplianceReminderAdmin(admin.ModelAdmin):
    list_display = ['startup', 'title', 'due_date', 'completed']
    list_filter = ['startup', 'completed']
    search_fields = ['startup__company_name', 'title']
    ordering = ['due_date']