from django.urls import path
from . import views

app_name = 'compliance'

urlpatterns = [
    # Dashboard
    path('', views.compliance_dashboard, name='compliance_dashboard'),
    
    # GST
    path('gst/', views.gst_dashboard, name='gst_dashboard'),
    path('gst/create/', views.gst_create, name='gst_create'),
    path('gst/edit/<int:pk>/', views.gst_edit, name='gst_edit'),
    path('gst/delete/<int:pk>/', views.gst_delete, name='gst_delete'),
    path('gst/mark-filed/<int:pk>/', views.gst_mark_filed, name='gst_mark_filed'),
    
    # TDS
    path('tds/', views.tds_dashboard, name='tds_dashboard'),
    path('tds/create/', views.tds_create, name='tds_create'),
    path('tds/edit/<int:pk>/', views.tds_edit, name='tds_edit'),
    path('tds/delete/<int:pk>/', views.tds_delete, name='tds_delete'),
    path('tds/mark-filed/<int:pk>/', views.tds_mark_filed, name='tds_mark_filed'),
    
    # PF
    path('pf/', views.pf_dashboard, name='pf_dashboard'),
    path('pf/create/', views.pf_create, name='pf_create'),
    path('pf/edit/<int:pk>/', views.pf_edit, name='pf_edit'),
    path('pf/delete/<int:pk>/', views.pf_delete, name='pf_delete'),
    path('pf/mark-paid/<int:pk>/', views.pf_mark_paid, name='pf_mark_paid'),
    
    # ESIC
    path('esic/', views.esic_dashboard, name='esic_dashboard'),
    path('esic/create/', views.esic_create, name='esic_create'),
    path('esic/edit/<int:pk>/', views.esic_edit, name='esic_edit'),
    path('esic/delete/<int:pk>/', views.esic_delete, name='esic_delete'),
    path('esic/mark-paid/<int:pk>/', views.esic_mark_paid, name='esic_mark_paid'),
    
    # MCA
    path('mca/', views.mca_dashboard, name='mca_dashboard'),
    path('mca/create/', views.mca_create, name='mca_create'),
    path('mca/edit/<int:pk>/', views.mca_edit, name='mca_edit'),
    path('mca/delete/<int:pk>/', views.mca_delete, name='mca_delete'),
    path('mca/mark-filed/<int:pk>/', views.mca_mark_filed, name='mca_mark_filed'),
    
    # Income Tax
    path('income-tax/', views.income_tax_dashboard, name='income_tax_dashboard'),
    path('income-tax/create/', views.income_tax_create, name='income_tax_create'),
    path('income-tax/edit/<int:pk>/', views.income_tax_edit, name='income_tax_edit'),
    path('income-tax/delete/<int:pk>/', views.income_tax_delete, name='income_tax_delete'),
    path('income-tax/mark-filed/<int:pk>/', views.income_tax_mark_filed, name='income_tax_mark_filed'),
    
    # Calendar & Reminders
    path('calendar/', views.compliance_calendar, name='compliance_calendar'),
    path('reminder/create/', views.reminder_create, name='reminder_create'),
    path('reminder/edit/<int:pk>/', views.reminder_edit, name='reminder_edit'),
    path('reminder/delete/<int:pk>/', views.reminder_delete, name='reminder_delete'),
    path('reminder/complete/<int:pk>/', views.reminder_complete, name='reminder_complete'),
]