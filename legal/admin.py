from django.contrib import admin
from .models import (
    FounderAgreement, EmploymentContract, NDA, VendorAgreement,
    ClientAgreement, Trademark, IPAssignment, ShareholderAgreement
)

@admin.register(FounderAgreement)
class FounderAgreementAdmin(admin.ModelAdmin):
    list_display = ['startup', 'title', 'created_at']
    list_filter = ['startup']
    search_fields = ['startup__company_name', 'title']
    ordering = ['-created_at']
    readonly_fields = ['created_at']

@admin.register(EmploymentContract)
class EmploymentContractAdmin(admin.ModelAdmin):
    list_display = ['startup', 'employee_name', 'designation', 'active']
    list_filter = ['startup', 'active']
    search_fields = ['startup__company_name', 'employee_name', 'designation']
    ordering = ['employee_name']

@admin.register(NDA)
class NDAAdmin(admin.ModelAdmin):
    list_display = ['startup', 'party_name', 'signed']
    list_filter = ['startup', 'signed']
    search_fields = ['startup__company_name', 'party_name']
    ordering = ['party_name']

@admin.register(VendorAgreement)
class VendorAgreementAdmin(admin.ModelAdmin):
    list_display = ['startup', 'vendor_name', 'active']
    list_filter = ['startup', 'active']
    search_fields = ['startup__company_name', 'vendor_name']
    ordering = ['vendor_name']

@admin.register(ClientAgreement)
class ClientAgreementAdmin(admin.ModelAdmin):
    list_display = ['startup', 'client_name', 'value']
    list_filter = ['startup']
    search_fields = ['startup__company_name', 'client_name']
    ordering = ['client_name']

@admin.register(Trademark)
class TrademarkAdmin(admin.ModelAdmin):
    list_display = ['startup', 'trademark_name', 'status', 'application_number']
    list_filter = ['startup', 'status']
    search_fields = ['startup__company_name', 'trademark_name', 'application_number']
    ordering = ['trademark_name']

@admin.register(IPAssignment)
class IPAssignmentAdmin(admin.ModelAdmin):
    list_display = ['startup', 'contributor']
    list_filter = ['startup']
    search_fields = ['startup__company_name', 'contributor']
    ordering = ['contributor']

@admin.register(ShareholderAgreement)
class ShareholderAgreementAdmin(admin.ModelAdmin):
    list_display = ['startup', 'created_at']
    list_filter = ['startup']
    search_fields = ['startup__company_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']