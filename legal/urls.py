from django.urls import path
from . import views

app_name = 'legal'

urlpatterns = [
    # Dashboard
    path('', views.legal_dashboard, name='legal_dashboard'),
    
    # Founder Agreements
    path('founders/', views.founder_agreements, name='founder_agreements'),
    path('founders/create/', views.founder_agreement_create, name='founder_agreement_create'),
    path('founders/delete/<int:pk>/', views.founder_agreement_delete, name='founder_agreement_delete'),
    
    # Employment Contracts
    path('contracts/', views.contracts, name='contracts'),
    path('contracts/create/', views.contract_create, name='contract_create'),
    path('contracts/edit/<int:pk>/', views.contract_edit, name='contract_edit'),
    path('contracts/delete/<int:pk>/', views.contract_delete, name='contract_delete'),
    path('contracts/toggle/<int:pk>/', views.contract_toggle_active, name='contract_toggle_active'),
    
    # NDAs
    path('nda/', views.nda, name='nda'),
    path('nda/create/', views.nda_create, name='nda_create'),
    path('nda/delete/<int:pk>/', views.nda_delete, name='nda_delete'),
    path('nda/toggle/<int:pk>/', views.nda_toggle_signed, name='nda_toggle_signed'),
    
    # Vendor Agreements
    path('vendors/', views.vendor_agreements, name='vendor_agreements'),
    path('vendors/create/', views.vendor_agreement_create, name='vendor_agreement_create'),
    path('vendors/delete/<int:pk>/', views.vendor_agreement_delete, name='vendor_agreement_delete'),
    path('vendors/toggle/<int:pk>/', views.vendor_agreement_toggle_active, name='vendor_agreement_toggle_active'),
    
    # Client Agreements
    path('clients/', views.client_agreements, name='client_agreements'),
    path('clients/create/', views.client_agreement_create, name='client_agreement_create'),
    path('clients/delete/<int:pk>/', views.client_agreement_delete, name='client_agreement_delete'),
    
    # Trademarks
    path('trademarks/', views.trademarks, name='trademarks'),
    path('trademarks/create/', views.trademark_create, name='trademark_create'),
    path('trademarks/edit/<int:pk>/', views.trademark_edit, name='trademark_edit'),
    path('trademarks/delete/<int:pk>/', views.trademark_delete, name='trademark_delete'),
    
    # IP Assignments
    path('ip/', views.ip_assignments, name='ip_assignments'),
    path('ip/create/', views.ip_assignment_create, name='ip_assignment_create'),
    path('ip/delete/<int:pk>/', views.ip_assignment_delete, name='ip_assignment_delete'),
    
    # Shareholder Agreements
    path('shareholders/', views.shareholders, name='shareholders'),
    path('shareholders/create/', views.shareholder_agreement_create, name='shareholder_agreement_create'),
    path('shareholders/delete/<int:pk>/', views.shareholder_agreement_delete, name='shareholder_agreement_delete'),
]