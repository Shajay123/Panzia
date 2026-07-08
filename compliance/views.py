from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from startups.models import StartupProfile
from .models import (
    GSTFiling, TDSFiling, PFContribution, ESICContribution,
    MCAFiling, IncomeTaxFiling, ComplianceReminder
)
from .forms import (
    GSTFilingForm, TDSFilingForm, PFContributionForm, ESICContributionForm,
    MCAFilingForm, IncomeTaxFilingForm, ComplianceReminderForm
)

# Helper functions
def check_compliance_access(request):
    """Check if user has access to compliance module."""
    return request.user.has_perm('finance.can_view_compliance')

def get_user_startup(request):
    """Get the startup associated with the user."""
    try:
        return StartupProfile.objects.get(users=request.user)
    except StartupProfile.DoesNotExist:
        return None

def check_hr_access(request):
    """Check if user has HR access."""
    return request.user.has_perm('hr.can_view_hr')

# ============================================
# COMPLIANCE DASHBOARD
# ============================================

@login_required
def compliance_dashboard(request):
    """Compliance Dashboard - Overview of all compliance activities."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        context = {
            'startup': None,
            'total_gst': 0,
            'total_tds': 0,
            'total_pf': 0,
            'total_esic': 0,
            'total_mca': 0,
            'total_income_tax': 0,
            'pending_gst': 0,
            'pending_tds': 0,
            'pending_pf': 0,
            'pending_esic': 0,
            'pending_mca': 0,
            'pending_income_tax': 0,
            'overdue_gst': 0,
            'overdue_tds': 0,
            'overdue_pf': 0,
            'overdue_esic': 0,
            'overdue_mca': 0,
            'overdue_income_tax': 0,
            'upcoming_reminders': [],
            'recent_filings': [],
            'page_title': 'Compliance Dashboard',
            'page_icon': '📋',
            'page_subtitle': 'Track your compliance and regulatory filings',
            'is_hr': check_hr_access(request),
            'no_startup': True,
        }
        return render(request, 'compliance/dashboard.html', context)
    
    today = timezone.now().date()
    
    # GST Filings
    gst_filings = GSTFiling.objects.filter(startup=startup)
    total_gst = gst_filings.count()
    pending_gst = gst_filings.filter(status='Pending').count()
    overdue_gst = gst_filings.filter(status='Overdue').count()
    
    # TDS Filings
    tds_filings = TDSFiling.objects.filter(startup=startup)
    total_tds = tds_filings.count()
    pending_tds = tds_filings.filter(status='Pending').count()
    overdue_tds = tds_filings.filter(status='Overdue').count()
    
    # PF Contributions
    pf_contributions = PFContribution.objects.filter(startup=startup)
    total_pf = pf_contributions.count()
    pending_pf = pf_contributions.filter(paid=False).count()
    overdue_pf = pf_contributions.filter(due_date__lt=today, paid=False).count()
    
    # ESIC Contributions
    esic_contributions = ESICContribution.objects.filter(startup=startup)
    total_esic = esic_contributions.count()
    pending_esic = esic_contributions.filter(paid=False).count()
    overdue_esic = esic_contributions.filter(due_date__lt=today, paid=False).count()
    
    # MCA Filings
    mca_filings = MCAFiling.objects.filter(startup=startup)
    total_mca = mca_filings.count()
    pending_mca = mca_filings.filter(status='Pending').count()
    overdue_mca = mca_filings.filter(due_date__lt=today, status='Pending').count()
    
    # Income Tax Filings
    income_tax_filings = IncomeTaxFiling.objects.filter(startup=startup)
    total_income_tax = income_tax_filings.count()
    pending_income_tax = income_tax_filings.filter(status='Pending').count()
    overdue_income_tax = income_tax_filings.filter(due_date__lt=today, status='Pending').count()
    
    # Upcoming Reminders (next 30 days)
    upcoming_reminders = ComplianceReminder.objects.filter(
        startup=startup,
        completed=False,
        due_date__gte=today
    ).order_by('due_date')[:10]
    
    # Recent Filings
    recent_filings = []
    
    # Get recent GST filings
    recent_gst = gst_filings.filter(filed=True).order_by('-filed_date')[:3]
    for filing in recent_gst:
        recent_filings.append({
            'type': 'GST',
            'title': f"{filing.get_return_type_display()} - {filing.month} {filing.year}",
            'date': filing.filed_date,
            'status': 'Filed'
        })
    
    # Get recent TDS filings
    recent_tds = tds_filings.filter(filed=True).order_by('-filed_date')[:3]
    for filing in recent_tds:
        recent_filings.append({
            'type': 'TDS',
            'title': f"TDS {filing.quarter}-{filing.year}",
            'date': filing.filed_date,
            'status': 'Filed'
        })
    
    # Sort by date
    recent_filings.sort(key=lambda x: x['date'] if x['date'] else datetime.min.date(), reverse=True)
    recent_filings = recent_filings[:10]
    
    context = {
        'startup': startup,
        'total_gst': total_gst,
        'total_tds': total_tds,
        'total_pf': total_pf,
        'total_esic': total_esic,
        'total_mca': total_mca,
        'total_income_tax': total_income_tax,
        'pending_gst': pending_gst,
        'pending_tds': pending_tds,
        'pending_pf': pending_pf,
        'pending_esic': pending_esic,
        'pending_mca': pending_mca,
        'pending_income_tax': pending_income_tax,
        'overdue_gst': overdue_gst,
        'overdue_tds': overdue_tds,
        'overdue_pf': overdue_pf,
        'overdue_esic': overdue_esic,
        'overdue_mca': overdue_mca,
        'overdue_income_tax': overdue_income_tax,
        'upcoming_reminders': upcoming_reminders,
        'recent_filings': recent_filings,
        'page_title': 'Compliance Dashboard',
        'page_icon': '📋',
        'page_subtitle': 'Track your compliance and regulatory filings',
        'is_hr': check_hr_access(request),
        'no_startup': False,
    }
    return render(request, 'compliance/dashboard.html', context)

# ============================================
# GST VIEWS
# ============================================

@login_required
def gst_dashboard(request):
    """GST Dashboard - Manage all GST filings."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    gst_filings = GSTFiling.objects.filter(startup=startup).order_by('-year', '-month')
    
    total_amount = gst_filings.aggregate(Sum('turnover'))['turnover__sum'] or 0
    total_tax = gst_filings.aggregate(Sum('tax_payable'))['tax_payable__sum'] or 0
    
    context = {
        'gst_filings': gst_filings,
        'total_amount': total_amount,
        'total_tax': total_tax,
        'page_title': 'GST Management',
        'page_icon': '📊',
        'page_subtitle': 'Manage your GST filings',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/gst_dashboard.html', context)

@login_required
def gst_create(request):
    """Create a new GST filing."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    if request.method == 'POST':
        form = GSTFilingForm(request.POST)
        if form.is_valid():
            gst_filing = form.save(commit=False)
            gst_filing.startup = startup
            gst_filing.save()
            messages.success(request, f'GST filing for {gst_filing.month} {gst_filing.year} created successfully!')
            return redirect('compliance:gst_dashboard')
    else:
        form = GSTFilingForm()
    
    context = {
        'form': form,
        'page_title': 'Add GST Filing',
        'page_icon': '📊',
        'page_subtitle': 'Create a new GST filing entry',
        'is_edit': False,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/gst_form.html', context)

@login_required
def gst_edit(request, pk):
    """Edit a GST filing."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    gst_filing = get_object_or_404(GSTFiling, pk=pk, startup=startup)
    
    if request.method == 'POST':
        form = GSTFilingForm(request.POST, instance=gst_filing)
        if form.is_valid():
            form.save()
            messages.success(request, 'GST filing updated successfully!')
            return redirect('compliance:gst_dashboard')
    else:
        form = GSTFilingForm(instance=gst_filing)
    
    context = {
        'form': form,
        'gst_filing': gst_filing,
        'page_title': 'Edit GST Filing',
        'page_icon': '✏️',
        'page_subtitle': 'Update GST filing entry',
        'is_edit': True,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/gst_form.html', context)

@login_required
def gst_delete(request, pk):
    """Delete a GST filing."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    gst_filing = get_object_or_404(GSTFiling, pk=pk, startup=startup)
    
    if request.method == 'POST':
        gst_filing.delete()
        messages.success(request, 'GST filing deleted successfully!')
        return redirect('compliance:gst_dashboard')
    
    context = {
        'gst_filing': gst_filing,
        'page_title': 'Delete GST Filing',
        'page_icon': '🗑️',
        'page_subtitle': 'Confirm deletion of GST filing',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/gst_confirm_delete.html', context)

@login_required
def gst_mark_filed(request, pk):
    """Mark GST filing as filed."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    gst_filing = get_object_or_404(GSTFiling, pk=pk, startup=startup)
    
    if request.method == 'POST':
        gst_filing.filed = True
        gst_filing.status = 'Filed'
        gst_filing.filed_date = timezone.now().date()
        gst_filing.save()
        messages.success(request, 'GST filing marked as filed!')
        return redirect('compliance:gst_dashboard')
    
    context = {
        'gst_filing': gst_filing,
        'page_title': 'Mark as Filed',
        'page_icon': '✅',
        'page_subtitle': 'Confirm GST filing',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/gst_mark_filed.html', context)

# ============================================
# TDS VIEWS (similar pattern)
# ============================================

@login_required
def tds_dashboard(request):
    """TDS Dashboard - Manage all TDS filings."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    tds_filings = TDSFiling.objects.filter(startup=startup).order_by('-year', '-quarter')
    total_amount = tds_filings.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'tds_filings': tds_filings,
        'total_amount': total_amount,
        'page_title': 'TDS Management',
        'page_icon': '📊',
        'page_subtitle': 'Manage your TDS filings',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/tds_dashboard.html', context)

@login_required
def tds_create(request):
    """Create a new TDS filing."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    if request.method == 'POST':
        form = TDSFilingForm(request.POST)
        if form.is_valid():
            tds_filing = form.save(commit=False)
            tds_filing.startup = startup
            tds_filing.save()
            messages.success(request, 'TDS filing created successfully!')
            return redirect('compliance:tds_dashboard')
    else:
        form = TDSFilingForm()
    
    context = {
        'form': form,
        'page_title': 'Add TDS Filing',
        'page_icon': '📊',
        'page_subtitle': 'Create a new TDS filing entry',
        'is_edit': False,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/tds_form.html', context)

@login_required
def tds_edit(request, pk):
    """Edit a TDS filing."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    tds_filing = get_object_or_404(TDSFiling, pk=pk, startup=startup)
    
    if request.method == 'POST':
        form = TDSFilingForm(request.POST, instance=tds_filing)
        if form.is_valid():
            form.save()
            messages.success(request, 'TDS filing updated successfully!')
            return redirect('compliance:tds_dashboard')
    else:
        form = TDSFilingForm(instance=tds_filing)
    
    context = {
        'form': form,
        'tds_filing': tds_filing,
        'page_title': 'Edit TDS Filing',
        'page_icon': '✏️',
        'page_subtitle': 'Update TDS filing entry',
        'is_edit': True,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/tds_form.html', context)

@login_required
def tds_delete(request, pk):
    """Delete a TDS filing."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    tds_filing = get_object_or_404(TDSFiling, pk=pk, startup=startup)
    
    if request.method == 'POST':
        tds_filing.delete()
        messages.success(request, 'TDS filing deleted successfully!')
        return redirect('compliance:tds_dashboard')
    
    context = {
        'tds_filing': tds_filing,
        'page_title': 'Delete TDS Filing',
        'page_icon': '🗑️',
        'page_subtitle': 'Confirm deletion of TDS filing',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/tds_confirm_delete.html', context)

@login_required
def tds_mark_filed(request, pk):
    """Mark TDS filing as filed."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    tds_filing = get_object_or_404(TDSFiling, pk=pk, startup=startup)
    
    if request.method == 'POST':
        tds_filing.filed = True
        tds_filing.status = 'Filed'
        tds_filing.filed_date = timezone.now().date()
        tds_filing.save()
        messages.success(request, 'TDS filing marked as filed!')
        return redirect('compliance:tds_dashboard')
    
    context = {
        'tds_filing': tds_filing,
        'page_title': 'Mark as Filed',
        'page_icon': '✅',
        'page_subtitle': 'Confirm TDS filing',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/tds_mark_filed.html', context)

# ============================================
# PF VIEWS (similar pattern)
# ============================================

# ============================================
# PF VIEWS (Corrected)
# ============================================

@login_required
def pf_dashboard(request):
    """PF Dashboard - Manage all PF contributions."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    # Remove '-year' from order_by since PFContribution doesn't have a year field
    pf_contributions = PFContribution.objects.filter(startup=startup).order_by('-due_date')
    total_amount = pf_contributions.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Get today's date for overdue calculation
    today = timezone.now().date()
    
    context = {
        'pf_contributions': pf_contributions,
        'total_amount': total_amount,
        'today': today,
        'page_title': 'PF Management',
        'page_icon': '🏦',
        'page_subtitle': 'Manage your PF contributions',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/pf_dashboard.html', context)

@login_required
def pf_create(request):
    """Create a new PF contribution."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    if request.method == 'POST':
        form = PFContributionForm(request.POST)
        if form.is_valid():
            pf_contribution = form.save(commit=False)
            pf_contribution.startup = startup
            pf_contribution.save()
            messages.success(request, 'PF contribution created successfully!')
            return redirect('compliance:pf_dashboard')
    else:
        form = PFContributionForm()
    
    context = {
        'form': form,
        'page_title': 'Add PF Contribution',
        'page_icon': '🏦',
        'page_subtitle': 'Create a new PF contribution entry',
        'is_edit': False,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/pf_form.html', context)

@login_required
def pf_edit(request, pk):
    """Edit a PF contribution."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    pf_contribution = get_object_or_404(PFContribution, pk=pk, startup=startup)
    
    if request.method == 'POST':
        form = PFContributionForm(request.POST, instance=pf_contribution)
        if form.is_valid():
            form.save()
            messages.success(request, 'PF contribution updated successfully!')
            return redirect('compliance:pf_dashboard')
    else:
        form = PFContributionForm(instance=pf_contribution)
    
    context = {
        'form': form,
        'pf_contribution': pf_contribution,
        'page_title': 'Edit PF Contribution',
        'page_icon': '✏️',
        'page_subtitle': 'Update PF contribution entry',
        'is_edit': True,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/pf_form.html', context)

@login_required
def pf_delete(request, pk):
    """Delete a PF contribution."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    pf_contribution = get_object_or_404(PFContribution, pk=pk, startup=startup)
    
    if request.method == 'POST':
        pf_contribution.delete()
        messages.success(request, 'PF contribution deleted successfully!')
        return redirect('compliance:pf_dashboard')
    
    context = {
        'pf_contribution': pf_contribution,
        'page_title': 'Delete PF Contribution',
        'page_icon': '🗑️',
        'page_subtitle': 'Confirm deletion of PF contribution',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/pf_confirm_delete.html', context)

@login_required
def pf_mark_paid(request, pk):
    """Mark PF contribution as paid."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    pf_contribution = get_object_or_404(PFContribution, pk=pk, startup=startup)
    
    if request.method == 'POST':
        pf_contribution.paid = True
        pf_contribution.payment_date = timezone.now().date()  # Use timezone here
        pf_contribution.save()
        messages.success(request, 'PF contribution marked as paid!')
        return redirect('compliance:pf_dashboard')
    
    context = {
        'pf_contribution': pf_contribution,
        'page_title': 'Mark as Paid',
        'page_icon': '✅',
        'page_subtitle': 'Confirm PF payment',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/pf_mark_paid.html', context)

# ============================================
# ESIC VIEWS
# ============================================

@login_required
def esic_dashboard(request):
    """ESIC Dashboard - Manage all ESIC contributions."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    # Remove '-year' from order_by since ESICContribution doesn't have a year field
    esic_contributions = ESICContribution.objects.filter(startup=startup).order_by('-due_date')
    total_amount = esic_contributions.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Get today's date for overdue calculation
    today = timezone.now().date()
    
    context = {
        'esic_contributions': esic_contributions,
        'total_amount': total_amount,
        'today': today,
        'page_title': 'ESIC Management',
        'page_icon': '🏥',
        'page_subtitle': 'Manage your ESIC contributions',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/esic_dashboard.html', context)
@login_required
def esic_create(request):
    """Create a new ESIC contribution."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    if request.method == 'POST':
        form = ESICContributionForm(request.POST)
        if form.is_valid():
            esic_contribution = form.save(commit=False)
            esic_contribution.startup = startup
            esic_contribution.save()
            messages.success(request, 'ESIC contribution created successfully!')
            return redirect('compliance:esic_dashboard')
    else:
        form = ESICContributionForm()
    
    context = {
        'form': form,
        'page_title': 'Add ESIC Contribution',
        'page_icon': '🏥',
        'page_subtitle': 'Create a new ESIC contribution entry',
        'is_edit': False,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/esic_form.html', context)

@login_required
def esic_edit(request, pk):
    """Edit an ESIC contribution."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    esic_contribution = get_object_or_404(ESICContribution, pk=pk, startup=startup)
    
    if request.method == 'POST':
        form = ESICContributionForm(request.POST, instance=esic_contribution)
        if form.is_valid():
            form.save()
            messages.success(request, 'ESIC contribution updated successfully!')
            return redirect('compliance:esic_dashboard')
    else:
        form = ESICContributionForm(instance=esic_contribution)
    
    context = {
        'form': form,
        'esic_contribution': esic_contribution,
        'page_title': 'Edit ESIC Contribution',
        'page_icon': '✏️',
        'page_subtitle': 'Update ESIC contribution entry',
        'is_edit': True,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/esic_form.html', context)

@login_required
def esic_delete(request, pk):
    """Delete an ESIC contribution."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    esic_contribution = get_object_or_404(ESICContribution, pk=pk, startup=startup)
    
    if request.method == 'POST':
        esic_contribution.delete()
        messages.success(request, 'ESIC contribution deleted successfully!')
        return redirect('compliance:esic_dashboard')
    
    context = {
        'esic_contribution': esic_contribution,
        'page_title': 'Delete ESIC Contribution',
        'page_icon': '🗑️',
        'page_subtitle': 'Confirm deletion of ESIC contribution',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/esic_confirm_delete.html', context)

@login_required
def esic_mark_paid(request, pk):
    """Mark ESIC contribution as paid."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    esic_contribution = get_object_or_404(ESICContribution, pk=pk, startup=startup)
    
    if request.method == 'POST':
        esic_contribution.paid = True
        esic_contribution.payment_date = timezone.now().date()  # Use timezone here
        esic_contribution.save()
        messages.success(request, 'ESIC contribution marked as paid!')
        return redirect('compliance:esic_dashboard')
    
    context = {
        'esic_contribution': esic_contribution,
        'page_title': 'Mark as Paid',
        'page_icon': '✅',
        'page_subtitle': 'Confirm ESIC payment',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/esic_mark_paid.html', context)


# ============================================
# MCA VIEWS
# ============================================

@login_required
def mca_dashboard(request):
    """MCA Dashboard - Manage all MCA filings."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    mca_filings = MCAFiling.objects.filter(startup=startup).order_by('-due_date')
    
    context = {
        'mca_filings': mca_filings,
        'page_title': 'MCA Management',
        'page_icon': '📜',
        'page_subtitle': 'Manage your MCA filings',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/mca_dashboard.html', context)

@login_required
def mca_create(request):
    """Create a new MCA filing."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    if request.method == 'POST':
        form = MCAFilingForm(request.POST)
        if form.is_valid():
            mca_filing = form.save(commit=False)
            mca_filing.startup = startup
            mca_filing.save()
            messages.success(request, 'MCA filing created successfully!')
            return redirect('compliance:mca_dashboard')
    else:
        form = MCAFilingForm()
    
    context = {
        'form': form,
        'page_title': 'Add MCA Filing',
        'page_icon': '📜',
        'page_subtitle': 'Create a new MCA filing entry',
        'is_edit': False,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/mca_form.html', context)

@login_required
def mca_edit(request, pk):
    """Edit an MCA filing."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    mca_filing = get_object_or_404(MCAFiling, pk=pk, startup=startup)
    
    if request.method == 'POST':
        form = MCAFilingForm(request.POST, instance=mca_filing)
        if form.is_valid():
            form.save()
            messages.success(request, 'MCA filing updated successfully!')
            return redirect('compliance:mca_dashboard')
    else:
        form = MCAFilingForm(instance=mca_filing)
    
    context = {
        'form': form,
        'mca_filing': mca_filing,
        'page_title': 'Edit MCA Filing',
        'page_icon': '✏️',
        'page_subtitle': 'Update MCA filing entry',
        'is_edit': True,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/mca_form.html', context)

@login_required
def mca_delete(request, pk):
    """Delete an MCA filing."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    mca_filing = get_object_or_404(MCAFiling, pk=pk, startup=startup)
    
    if request.method == 'POST':
        mca_filing.delete()
        messages.success(request, 'MCA filing deleted successfully!')
        return redirect('compliance:mca_dashboard')
    
    context = {
        'mca_filing': mca_filing,
        'page_title': 'Delete MCA Filing',
        'page_icon': '🗑️',
        'page_subtitle': 'Confirm deletion of MCA filing',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/mca_confirm_delete.html', context)

@login_required
def mca_mark_filed(request, pk):
    """Mark MCA filing as filed."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    mca_filing = get_object_or_404(MCAFiling, pk=pk, startup=startup)
    
    if request.method == 'POST':
        mca_filing.filed = True
        mca_filing.status = 'Filed'
        mca_filing.filed_date = timezone.now().date()
        mca_filing.save()
        messages.success(request, 'MCA filing marked as filed!')
        return redirect('compliance:mca_dashboard')
    
    context = {
        'mca_filing': mca_filing,
        'page_title': 'Mark as Filed',
        'page_icon': '✅',
        'page_subtitle': 'Confirm MCA filing',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/mca_mark_filed.html', context)

# ============================================
# INCOME TAX VIEWS
# ============================================

@login_required
def income_tax_dashboard(request):
    """Income Tax Dashboard - Manage all Income Tax filings."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    income_tax_filings = IncomeTaxFiling.objects.filter(startup=startup).order_by('-assessment_year')
    total_tax = income_tax_filings.aggregate(Sum('tax_amount'))['tax_amount__sum'] or 0
    
    context = {
        'income_tax_filings': income_tax_filings,
        'total_tax': total_tax,
        'page_title': 'Income Tax Management',
        'page_icon': '💰',
        'page_subtitle': 'Manage your Income Tax filings',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/income_tax_dashboard.html', context)

@login_required
def income_tax_create(request):
    """Create a new Income Tax filing."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    if request.method == 'POST':
        form = IncomeTaxFilingForm(request.POST)
        if form.is_valid():
            income_tax_filing = form.save(commit=False)
            income_tax_filing.startup = startup
            income_tax_filing.save()
            messages.success(request, 'Income Tax filing created successfully!')
            return redirect('compliance:income_tax_dashboard')
    else:
        form = IncomeTaxFilingForm()
    
    context = {
        'form': form,
        'page_title': 'Add Income Tax Filing',
        'page_icon': '💰',
        'page_subtitle': 'Create a new Income Tax filing entry',
        'is_edit': False,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/income_tax_form.html', context)

@login_required
def income_tax_edit(request, pk):
    """Edit an Income Tax filing."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    income_tax_filing = get_object_or_404(IncomeTaxFiling, pk=pk, startup=startup)
    
    if request.method == 'POST':
        form = IncomeTaxFilingForm(request.POST, instance=income_tax_filing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Income Tax filing updated successfully!')
            return redirect('compliance:income_tax_dashboard')
    else:
        form = IncomeTaxFilingForm(instance=income_tax_filing)
    
    context = {
        'form': form,
        'income_tax_filing': income_tax_filing,
        'page_title': 'Edit Income Tax Filing',
        'page_icon': '✏️',
        'page_subtitle': 'Update Income Tax filing entry',
        'is_edit': True,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/income_tax_form.html', context)

@login_required
def income_tax_delete(request, pk):
    """Delete an Income Tax filing."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    income_tax_filing = get_object_or_404(IncomeTaxFiling, pk=pk, startup=startup)
    
    if request.method == 'POST':
        income_tax_filing.delete()
        messages.success(request, 'Income Tax filing deleted successfully!')
        return redirect('compliance:income_tax_dashboard')
    
    context = {
        'income_tax_filing': income_tax_filing,
        'page_title': 'Delete Income Tax Filing',
        'page_icon': '🗑️',
        'page_subtitle': 'Confirm deletion of Income Tax filing',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/income_tax_confirm_delete.html', context)

@login_required
def income_tax_mark_filed(request, pk):
    """Mark Income Tax filing as filed."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    income_tax_filing = get_object_or_404(IncomeTaxFiling, pk=pk, startup=startup)
    
    if request.method == 'POST':
        income_tax_filing.filed = True
        income_tax_filing.status = 'Filed'
        income_tax_filing.filed_date = timezone.now().date()
        income_tax_filing.save()
        messages.success(request, 'Income Tax filing marked as filed!')
        return redirect('compliance:income_tax_dashboard')
    
    context = {
        'income_tax_filing': income_tax_filing,
        'page_title': 'Mark as Filed',
        'page_icon': '✅',
        'page_subtitle': 'Confirm Income Tax filing',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/income_tax_mark_filed.html', context)

# ============================================
# REMINDER VIEWS
# ============================================

@login_required
def compliance_calendar(request):
    """Compliance Calendar - View all upcoming compliance deadlines."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    today = timezone.now().date()
    
    # Get all upcoming deadlines
    reminders = ComplianceReminder.objects.filter(
        startup=startup,
        completed=False
    ).order_by('due_date')
    
    # Get GST deadlines
    gst_deadlines = GSTFiling.objects.filter(
        startup=startup,
        filed=False,
        due_date__gte=today
    ).values('due_date', 'return_type', 'month', 'year')
    
    # Get TDS deadlines
    tds_deadlines = TDSFiling.objects.filter(
        startup=startup,
        filed=False,
        due_date__gte=today
    ).values('due_date', 'quarter', 'year')
    
    context = {
        'reminders': reminders,
        'gst_deadlines': gst_deadlines,
        'tds_deadlines': tds_deadlines,
        'page_title': 'Compliance Calendar',
        'page_icon': '📅',
        'page_subtitle': 'Track your compliance deadlines',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/calendar.html', context)

@login_required
def reminder_create(request):
    """Create a new compliance reminder."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    if request.method == 'POST':
        form = ComplianceReminderForm(request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.startup = startup
            reminder.save()
            messages.success(request, 'Reminder created successfully!')
            return redirect('compliance:compliance_calendar')
    else:
        form = ComplianceReminderForm()
    
    context = {
        'form': form,
        'page_title': 'Add Reminder',
        'page_icon': '🔔',
        'page_subtitle': 'Create a new compliance reminder',
        'is_edit': False,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/reminder_form.html', context)

@login_required
def reminder_edit(request, pk):
    """Edit a compliance reminder."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    reminder = get_object_or_404(ComplianceReminder, pk=pk, startup=startup)
    
    if request.method == 'POST':
        form = ComplianceReminderForm(request.POST, instance=reminder)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reminder updated successfully!')
            return redirect('compliance:compliance_calendar')
    else:
        form = ComplianceReminderForm(instance=reminder)
    
    context = {
        'form': form,
        'reminder': reminder,
        'page_title': 'Edit Reminder',
        'page_icon': '✏️',
        'page_subtitle': 'Update compliance reminder',
        'is_edit': True,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/reminder_form.html', context)

@login_required
def reminder_delete(request, pk):
    """Delete a compliance reminder."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    reminder = get_object_or_404(ComplianceReminder, pk=pk, startup=startup)
    
    if request.method == 'POST':
        reminder.delete()
        messages.success(request, 'Reminder deleted successfully!')
        return redirect('compliance:compliance_calendar')
    
    context = {
        'reminder': reminder,
        'page_title': 'Delete Reminder',
        'page_icon': '🗑️',
        'page_subtitle': 'Confirm deletion of reminder',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/reminder_confirm_delete.html', context)

@login_required
def reminder_complete(request, pk):
    """Mark a compliance reminder as completed."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('compliance:compliance_dashboard')
    
    reminder = get_object_or_404(ComplianceReminder, pk=pk, startup=startup)
    
    if request.method == 'POST':
        reminder.completed = True
        reminder.save()
        messages.success(request, 'Reminder marked as completed!')
        return redirect('compliance:compliance_calendar')
    
    context = {
        'reminder': reminder,
        'page_title': 'Complete Reminder',
        'page_icon': '✅',
        'page_subtitle': 'Confirm reminder completion',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'compliance/reminder_complete.html', context)