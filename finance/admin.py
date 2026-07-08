# finance/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum
from decimal import Decimal
from .models import (
    Income, Expense, Invoice, Receivable, 
    Vendor, AccountsPayable, Reimbursement
)


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title', 'client', 'amount_display', 
        'received_date', 'startup_name', 'created_at'
    ]
    list_filter = ['startup', 'received_date', 'created_at']
    search_fields = ['title', 'client', 'startup__company_name']
    ordering = ['-received_date', '-created_at']
    date_hierarchy = 'received_date'
    list_per_page = 50
    
    fieldsets = (
        ('Income Information', {
            'fields': ('startup', 'title', 'client', 'amount', 'received_date')
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)
    
    def amount_display(self, obj):
        try:
            amount = float(obj.amount) if obj.amount else 0
            return format_html(
                '<span style="color: #34d399; font-weight: bold;">₹{:,.2f}</span>',
                amount
            )
        except (ValueError, TypeError):
            return format_html(
                '<span style="color: #34d399; font-weight: bold;">₹0.00</span>'
            )
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'
    
    def startup_name(self, obj):
        return obj.startup.company_name
    startup_name.short_description = 'Startup'
    startup_name.admin_order_field = 'startup__company_name'


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title', 'category_badge', 'amount_display', 
        'expense_date', 'startup_name', 'created_at'
    ]
    list_filter = ['startup', 'category', 'expense_date', 'created_at']
    search_fields = ['title', 'startup__company_name']
    ordering = ['-expense_date', '-created_at']
    date_hierarchy = 'expense_date'
    list_per_page = 50
    
    fieldsets = (
        ('Expense Information', {
            'fields': ('startup', 'title', 'category', 'amount', 'expense_date')
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)
    
    def amount_display(self, obj):
        try:
            amount = float(obj.amount) if obj.amount else 0
            return format_html(
                '<span style="color: #f87171; font-weight: bold;">₹{:,.2f}</span>',
                amount
            )
        except (ValueError, TypeError):
            return format_html(
                '<span style="color: #f87171; font-weight: bold;">₹0.00</span>'
            )
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'
    
    def category_badge(self, obj):
        colors = {
            'Salary': '#34d399',
            'Software': '#60a5fa',
            'Marketing': '#f472b6',
            'Office': '#fbbf24',
            'Travel': '#a78bfa',
            'Other': '#94a3b8',
        }
        color = colors.get(obj.category, '#94a3b8')
        return format_html(
            '<span style="background: {}; color: #0a0618; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">{}</span>',
            color, obj.category
        )
    category_badge.short_description = 'Category'
    category_badge.admin_order_field = 'category'
    
    def startup_name(self, obj):
        return obj.startup.company_name
    startup_name.short_description = 'Startup'
    startup_name.admin_order_field = 'startup__company_name'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'invoice_number', 'client_name', 'amount_display', 
        'status_badge', 'due_date', 'startup_name', 'created_at'
    ]
    list_filter = ['startup', 'status', 'due_date', 'created_at']
    search_fields = ['invoice_number', 'client_name', 'startup__company_name']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    list_per_page = 50
    readonly_fields = ('invoice_number', 'created_at')
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('startup', 'invoice_number', 'client_name', 'amount', 'due_date', 'status')
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def amount_display(self, obj):
        try:
            amount = float(obj.amount) if obj.amount else 0
            return format_html(
                '<span style="color: #e8edf5; font-weight: bold;">₹{:,.2f}</span>',
                amount
            )
        except (ValueError, TypeError):
            return format_html(
                '<span style="color: #e8edf5; font-weight: bold;">₹0.00</span>'
            )
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'
    
    def status_badge(self, obj):
        colors = {
            'Paid': ('#34d399', '✅ Paid'),
            'Sent': ('#60a5fa', '📤 Sent'),
            'Draft': ('#94a3b8', '📝 Draft'),
            'Overdue': ('#f87171', '⚠️ Overdue'),
        }
        color, label = colors.get(obj.status, ('#94a3b8', obj.status))
        return format_html(
            '<span style="background: {}; color: #0a0618; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">{}</span>',
            color, label
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def startup_name(self, obj):
        return obj.startup.company_name
    startup_name.short_description = 'Startup'
    startup_name.admin_order_field = 'startup__company_name'
    
    actions = ['mark_as_paid', 'mark_as_sent', 'mark_as_overdue']
    
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status='Paid')
        for invoice in queryset:
            Receivable.objects.filter(invoice=invoice).update(paid=True)
        self.message_user(request, f'{updated} invoices marked as Paid.')
    mark_as_paid.short_description = 'Mark selected invoices as Paid'
    
    def mark_as_sent(self, request, queryset):
        updated = queryset.update(status='Sent')
        self.message_user(request, f'{updated} invoices marked as Sent.')
    mark_as_sent.short_description = 'Mark selected invoices as Sent'
    
    def mark_as_overdue(self, request, queryset):
        updated = queryset.update(status='Overdue')
        self.message_user(request, f'{updated} invoices marked as Overdue.')
    mark_as_overdue.short_description = 'Mark selected invoices as Overdue'


@admin.register(Receivable)
class ReceivableAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'invoice_link', 'amount_display', 
        'paid_status', 'client_name', 'startup_name'
    ]
    list_filter = ['paid', 'invoice__startup', 'invoice__due_date']
    search_fields = ['invoice__invoice_number', 'invoice__client_name']
    ordering = ['-invoice__created_at']
    list_per_page = 50
    
    fieldsets = (
        ('Receivable Information', {
            'fields': ('invoice', 'amount_due', 'paid')
        }),
    )
    
    def invoice_link(self, obj):
        url = reverse('admin:finance_invoice_change', args=[obj.invoice.id])
        return format_html(
            '<a href="{}" style="color: #a78bfa; text-decoration: none;">{}</a>',
            url, obj.invoice.invoice_number
        )
    invoice_link.short_description = 'Invoice'
    
    def amount_display(self, obj):
        try:
            amount = float(obj.amount_due) if obj.amount_due else 0
            color = '#34d399' if obj.paid else '#fbbf24'
            return format_html(
                '<span style="color: {}; font-weight: bold;">₹{:,.2f}</span>',
                color, amount
            )
        except (ValueError, TypeError):
            return format_html(
                '<span style="color: #94a3b8; font-weight: bold;">₹0.00</span>'
            )
    amount_display.short_description = 'Amount Due'
    amount_display.admin_order_field = 'amount_due'
    
    def paid_status(self, obj):
        if obj.paid:
            return format_html(
                '<span style="color: #34d399; font-weight: 600;">✅ Paid</span>'
            )
        return format_html(
            '<span style="color: #fbbf24; font-weight: 600;">⏳ Pending</span>'
        )
    paid_status.short_description = 'Status'
    paid_status.admin_order_field = 'paid'
    
    def client_name(self, obj):
        return obj.invoice.client_name
    client_name.short_description = 'Client'
    
    def startup_name(self, obj):
        return obj.invoice.startup.company_name
    startup_name.short_description = 'Startup'
    
    actions = ['mark_as_paid']
    
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(paid=True)
        for receivable in queryset:
            invoice = receivable.invoice
            if invoice.status != 'Paid':
                invoice.status = 'Paid'
                invoice.save()
        self.message_user(request, f'{updated} receivables marked as Paid.')
    mark_as_paid.short_description = 'Mark selected as Paid'


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'vendor_name', 'phone', 'email', 'startup_name', 
        'payable_count', 'total_payable'
    ]
    list_filter = ['startup']
    search_fields = ['vendor_name', 'phone', 'email', 'startup__company_name']
    ordering = ['vendor_name']
    list_per_page = 50
    
    fieldsets = (
        ('Vendor Information', {
            'fields': ('startup', 'vendor_name', 'phone', 'email')
        }),
    )
    
    def startup_name(self, obj):
        return obj.startup.company_name
    startup_name.short_description = 'Startup'
    startup_name.admin_order_field = 'startup__company_name'
    
    def payable_count(self, obj):
        return AccountsPayable.objects.filter(vendor=obj).count()
    payable_count.short_description = 'Payables'
    
    def total_payable(self, obj):
        total = AccountsPayable.objects.filter(vendor=obj).aggregate(Sum('amount'))['amount__sum'] or 0
        try:
            amount = float(total) if total else 0
            return format_html(
                '<span style="color: #f87171;">₹{:,.2f}</span>',
                amount
            )
        except (ValueError, TypeError):
            return format_html(
                '<span style="color: #f87171;">₹0.00</span>'
            )
    total_payable.short_description = 'Total Payable'


@admin.register(AccountsPayable)
class AccountsPayableAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'vendor_link', 'amount_display', 
        'due_date', 'paid_status', 'startup_name'
    ]
    list_filter = ['paid', 'vendor__startup', 'due_date']
    search_fields = ['vendor__vendor_name']
    ordering = ['due_date']
    list_per_page = 50
    
    fieldsets = (
        ('Payable Information', {
            'fields': ('vendor', 'amount', 'due_date', 'paid')
        }),
    )
    
    def vendor_link(self, obj):
        url = reverse('admin:finance_vendor_change', args=[obj.vendor.id])
        return format_html(
            '<a href="{}" style="color: #a78bfa; text-decoration: none;">{}</a>',
            url, obj.vendor.vendor_name
        )
    vendor_link.short_description = 'Vendor'
    
    def amount_display(self, obj):
        try:
            amount = float(obj.amount) if obj.amount else 0
            color = '#34d399' if obj.paid else '#f87171'
            return format_html(
                '<span style="color: {}; font-weight: bold;">₹{:,.2f}</span>',
                color, amount
            )
        except (ValueError, TypeError):
            return format_html(
                '<span style="color: #94a3b8; font-weight: bold;">₹0.00</span>'
            )
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'
    
    def paid_status(self, obj):
        if obj.paid:
            return format_html(
                '<span style="color: #34d399; font-weight: 600;">✅ Paid</span>'
            )
        return format_html(
            '<span style="color: #f87171; font-weight: 600;">⏳ Pending</span>'
        )
    paid_status.short_description = 'Status'
    paid_status.admin_order_field = 'paid'
    
    def startup_name(self, obj):
        return obj.vendor.startup.company_name
    startup_name.short_description = 'Startup'
    
    actions = ['mark_as_paid']
    
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(paid=True)
        self.message_user(request, f'{updated} payables marked as Paid.')
    mark_as_paid.short_description = 'Mark selected as Paid'


@admin.register(Reimbursement)
class ReimbursementAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'employee_name', 'amount_display', 
        'reason_truncated', 'approval_status', 'startup_name', 'created_at'
    ]
    list_filter = ['startup', 'approved', 'created_at']
    search_fields = ['employee__username', 'employee__first_name', 'employee__last_name', 'reason']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    list_per_page = 50
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Reimbursement Information', {
            'fields': ('startup', 'employee', 'amount', 'reason', 'approved')
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def employee_name(self, obj):
        return obj.employee.get_full_name() or obj.employee.username
    employee_name.short_description = 'Employee'
    employee_name.admin_order_field = 'employee__username'
    
    def amount_display(self, obj):
        try:
            amount = float(obj.amount) if obj.amount else 0
            color = '#34d399' if obj.approved else '#fbbf24'
            return format_html(
                '<span style="color: {}; font-weight: bold;">₹{:,.2f}</span>',
                color, amount
            )
        except (ValueError, TypeError):
            return format_html(
                '<span style="color: #94a3b8; font-weight: bold;">₹0.00</span>'
            )
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'
    
    def reason_truncated(self, obj):
        return obj.reason[:50] + '...' if len(obj.reason) > 50 else obj.reason
    reason_truncated.short_description = 'Reason'
    
    def approval_status(self, obj):
        if obj.approved:
            return format_html(
                '<span style="color: #34d399; font-weight: 600;">✅ Approved</span>'
            )
        return format_html(
            '<span style="color: #fbbf24; font-weight: 600;">⏳ Pending</span>'
        )
    approval_status.short_description = 'Status'
    approval_status.admin_order_field = 'approved'
    
    def startup_name(self, obj):
        return obj.startup.company_name
    startup_name.short_description = 'Startup'
    startup_name.admin_order_field = 'startup__company_name'
    
    actions = ['approve_selected']
    
    def approve_selected(self, request, queryset):
        updated = queryset.update(approved=True)
        self.message_user(request, f'{updated} reimbursements approved.')
    approve_selected.short_description = 'Approve selected reimbursements'


# ============================================
# INLINE ADMIN CLASSES
# ============================================

class ReceivableInline(admin.TabularInline):
    model = Receivable
    extra = 0
    fields = ['amount_due', 'paid']
    readonly_fields = ['amount_due']
    
    def has_add_permission(self, request, obj=None):
        return False


class AccountsPayableInline(admin.TabularInline):
    model = AccountsPayable
    extra = 0
    fields = ['amount', 'due_date', 'paid']
    readonly_fields = ['amount']