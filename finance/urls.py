# finance/urls.py

from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    # Dashboard
    path('', views.finance_dashboard, name='finance_dashboard'),
    
    # Income
    path('income/', views.income_list, name='income_list'),
    path('income/create/', views.income_create, name='income_create'),
    path('income/<int:pk>/edit/', views.income_edit, name='income_edit'),
    path('income/<int:pk>/delete/', views.income_delete, name='income_delete'),
    
    # Expenses
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    
    # Invoices
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/edit/', views.invoice_edit, name='invoice_edit'),
    path('invoices/<int:pk>/delete/', views.invoice_delete, name='invoice_delete'),
    
    # Accounts Receivable
    path('receivable/', views.receivable_list, name='receivable_list'),
    path('receivable/<int:pk>/mark-paid/', views.receivable_mark_paid, name='receivable_mark_paid'),
    
    # Vendors
    path('vendors/', views.vendor_list, name='vendor_list'),
    path('vendors/create/', views.vendor_create, name='vendor_create'),
    path('vendors/<int:pk>/edit/', views.vendor_edit, name='vendor_edit'),
    path('vendors/<int:pk>/delete/', views.vendor_delete, name='vendor_delete'),
    
    # Accounts Payable
    path('payable/', views.payable_list, name='payable_list'),
    path('payable/create/', views.payable_create, name='payable_create'),
    path('payable/<int:pk>/edit/', views.payable_edit, name='payable_edit'),
    path('payable/<int:pk>/delete/', views.payable_delete, name='payable_delete'),
    path('payable/<int:pk>/mark-paid/', views.payable_mark_paid, name='payable_mark_paid'),
    
    # Reimbursements
    path('reimbursements/', views.reimbursement_list, name='reimbursement_list'),
    path('reimbursements/create/', views.reimbursement_create, name='reimbursement_create'),
    path('reimbursements/<int:pk>/edit/', views.reimbursement_edit, name='reimbursement_edit'),
    path('reimbursements/<int:pk>/delete/', views.reimbursement_delete, name='reimbursement_delete'),
    path('reimbursements/<int:pk>/approve/', views.reimbursement_approve, name='reimbursement_approve'),
    
    # Reports
    path('profit-loss/', views.profit_loss, name='profit_loss'),
    path('cash-flow/', views.cash_flow, name='cash_flow'),
]