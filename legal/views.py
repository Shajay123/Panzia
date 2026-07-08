from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone

from startups.models import StartupProfile
from .models import (
    FounderAgreement, EmploymentContract, NDA, VendorAgreement,
    ClientAgreement, Trademark, IPAssignment, ShareholderAgreement
)

# Helper functions
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
# LEGAL DASHBOARD
# ============================================

@login_required
def legal_dashboard(request):
    """Legal Dashboard - Overview of all legal documents."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        context = {
            'startup': None,
            'total_founders': 0,
            'total_contracts': 0,
            'total_nda': 0,
            'total_vendors': 0,
            'total_clients': 0,
            'total_trademarks': 0,
            'total_ip': 0,
            'total_shareholders': 0,
            'signed_nda': 0,
            'active_contracts': 0,
            'active_vendors': 0,
            'trademark_applied': 0,
            'trademark_registered': 0,
            'recent_documents': [],
            'page_title': 'Legal Dashboard',
            'page_icon': '⚖️',
            'page_subtitle': 'Manage your legal documents and agreements',
            'is_hr': check_hr_access(request),
            'no_startup': True,
        }
        return render(request, 'legal/dashboard.html', context)
    
    # Get counts
    total_founders = FounderAgreement.objects.filter(startup=startup).count()
    total_contracts = EmploymentContract.objects.filter(startup=startup).count()
    total_nda = NDA.objects.filter(startup=startup).count()
    total_vendors = VendorAgreement.objects.filter(startup=startup).count()
    total_clients = ClientAgreement.objects.filter(startup=startup).count()
    total_trademarks = Trademark.objects.filter(startup=startup).count()
    total_ip = IPAssignment.objects.filter(startup=startup).count()
    total_shareholders = ShareholderAgreement.objects.filter(startup=startup).count()
    
    # Status counts
    signed_nda = NDA.objects.filter(startup=startup, signed=True).count()
    active_contracts = EmploymentContract.objects.filter(startup=startup, active=True).count()
    active_vendors = VendorAgreement.objects.filter(startup=startup, active=True).count()
    trademark_applied = Trademark.objects.filter(startup=startup, status='Applied').count()
    trademark_registered = Trademark.objects.filter(startup=startup, status='Registered').count()
    
    # Recent documents (combine all types)
    recent_documents = []
    
    # Get current time for sorting
    current_time = timezone.now()
    
    # Get recent founder agreements
    recent_founders = FounderAgreement.objects.filter(startup=startup).order_by('-created_at')[:3]
    for doc in recent_founders:
        recent_documents.append({
            'type': 'Founder Agreement',
            'title': doc.title,
            'date': doc.created_at,
            'icon': '👥'
        })
    
    # Get recent contracts - use a default date since contracts don't have created_at
    recent_contracts = EmploymentContract.objects.filter(startup=startup).order_by('-id')[:3]
    for doc in recent_contracts:
        # Use current_time as fallback for sorting
        recent_documents.append({
            'type': 'Employment Contract',
            'title': f"{doc.employee_name} - {doc.designation}",
            'date': current_time,  # Use current_time as fallback
            'icon': '📄'
        })
    
    # Get recent NDAs - use a default date since NDAs don't have created_at
    recent_ndas = NDA.objects.filter(startup=startup).order_by('-id')[:3]
    for doc in recent_ndas:
        recent_documents.append({
            'type': 'NDA',
            'title': f"NDA with {doc.party_name}",
            'date': current_time,  # Use current_time as fallback
            'icon': '🔒'
        })
    
    # Sort by date (all are now datetime objects)
    recent_documents.sort(key=lambda x: x['date'] if x['date'] else current_time, reverse=True)
    recent_documents = recent_documents[:5]
    
    context = {
        'startup': startup,
        'total_founders': total_founders,
        'total_contracts': total_contracts,
        'total_nda': total_nda,
        'total_vendors': total_vendors,
        'total_clients': total_clients,
        'total_trademarks': total_trademarks,
        'total_ip': total_ip,
        'total_shareholders': total_shareholders,
        'signed_nda': signed_nda,
        'active_contracts': active_contracts,
        'active_vendors': active_vendors,
        'trademark_applied': trademark_applied,
        'trademark_registered': trademark_registered,
        'recent_documents': recent_documents,
        'page_title': 'Legal Dashboard',
        'page_icon': '⚖️',
        'page_subtitle': 'Manage your legal documents and agreements',
        'is_hr': check_hr_access(request),
        'no_startup': False,
    }
    return render(request, 'legal/dashboard.html', context)

    
# ============================================
# FOUNDER AGREEMENTS
# ============================================

@login_required
def founder_agreements(request):
    """List all founder agreements."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    founders = FounderAgreement.objects.filter(startup=startup).order_by('-created_at')
    
    context = {
        'founders': founders,
        'page_title': 'Founder Agreements',
        'page_icon': '👥',
        'page_subtitle': 'Manage founder agreements',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/founder_agreements.html', context)

@login_required
def founder_agreement_create(request):
    """Create a new founder agreement."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        document = request.FILES.get('document')
        
        if not all([title, document]):
            messages.error(request, 'All fields are required.')
            return redirect('legal:founder_agreement_create')
        
        FounderAgreement.objects.create(
            startup=startup,
            title=title,
            document=document
        )
        messages.success(request, f'Founder agreement "{title}" created successfully!')
        return redirect('legal:founder_agreements')
    
    context = {
        'page_title': 'Add Founder Agreement',
        'page_icon': '👥',
        'page_subtitle': 'Upload a new founder agreement',
        'is_edit': False,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/founder_agreement_form.html', context)

@login_required
def founder_agreement_delete(request, pk):
    """Delete a founder agreement."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    founder = get_object_or_404(FounderAgreement, pk=pk, startup=startup)
    
    if request.method == 'POST':
        title = founder.title
        founder.delete()
        messages.success(request, f'Founder agreement "{title}" deleted successfully!')
        return redirect('legal:founder_agreements')
    
    context = {
        'founder': founder,
        'page_title': 'Delete Founder Agreement',
        'page_icon': '🗑️',
        'page_subtitle': 'Confirm deletion of founder agreement',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/founder_agreement_confirm_delete.html', context)

# ============================================
# EMPLOYMENT CONTRACTS
# ============================================

@login_required
def contracts(request):
    """List all employment contracts."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    contracts = EmploymentContract.objects.filter(startup=startup).order_by('employee_name')
    
    context = {
        'contracts': contracts,
        'page_title': 'Employment Contracts',
        'page_icon': '📄',
        'page_subtitle': 'Manage employee contracts',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/contracts.html', context)

@login_required
def contract_create(request):
    """Create a new employment contract."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    if request.method == 'POST':
        employee_name = request.POST.get('employee_name')
        designation = request.POST.get('designation')
        contract_file = request.FILES.get('contract_file')
        
        if not all([employee_name, designation, contract_file]):
            messages.error(request, 'All fields are required.')
            return redirect('legal:contract_create')
        
        EmploymentContract.objects.create(
            startup=startup,
            employee_name=employee_name,
            designation=designation,
            contract_file=contract_file
        )
        messages.success(request, f'Contract for "{employee_name}" created successfully!')
        return redirect('legal:contracts')
    
    context = {
        'page_title': 'Add Employment Contract',
        'page_icon': '📄',
        'page_subtitle': 'Upload a new employment contract',
        'is_edit': False,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/contract_form.html', context)

@login_required
def contract_edit(request, pk):
    """Edit an employment contract."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    contract = get_object_or_404(EmploymentContract, pk=pk, startup=startup)
    
    if request.method == 'POST':
        contract.employee_name = request.POST.get('employee_name')
        contract.designation = request.POST.get('designation')
        if request.FILES.get('contract_file'):
            contract.contract_file = request.FILES.get('contract_file')
        contract.save()
        messages.success(request, f'Contract for "{contract.employee_name}" updated successfully!')
        return redirect('legal:contracts')
    
    context = {
        'contract': contract,
        'page_title': 'Edit Employment Contract',
        'page_icon': '✏️',
        'page_subtitle': 'Update employment contract',
        'is_edit': True,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/contract_form.html', context)

@login_required
def contract_delete(request, pk):
    """Delete an employment contract."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    contract = get_object_or_404(EmploymentContract, pk=pk, startup=startup)
    
    if request.method == 'POST':
        employee_name = contract.employee_name
        contract.delete()
        messages.success(request, f'Contract for "{employee_name}" deleted successfully!')
        return redirect('legal:contracts')
    
    context = {
        'contract': contract,
        'page_title': 'Delete Employment Contract',
        'page_icon': '🗑️',
        'page_subtitle': 'Confirm deletion of employment contract',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/contract_confirm_delete.html', context)

@login_required
def contract_toggle_active(request, pk):
    """Toggle contract active status."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    contract = get_object_or_404(EmploymentContract, pk=pk, startup=startup)
    contract.active = not contract.active
    contract.save()
    
    status = "activated" if contract.active else "deactivated"
    messages.success(request, f'Contract for "{contract.employee_name}" {status} successfully!')
    return redirect('legal:contracts')

# ============================================
# NDA VIEWS
# ============================================

@login_required
def nda(request):
    """List all NDAs."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    ndas = NDA.objects.filter(startup=startup).order_by('party_name')
    
    context = {
        'ndas': ndas,
        'page_title': 'NDAs',
        'page_icon': '🔒',
        'page_subtitle': 'Manage Non-Disclosure Agreements',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/nda.html', context)

@login_required
def nda_create(request):
    """Create a new NDA."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    if request.method == 'POST':
        party_name = request.POST.get('party_name')
        file = request.FILES.get('file')
        
        if not all([party_name, file]):
            messages.error(request, 'All fields are required.')
            return redirect('legal:nda_create')
        
        NDA.objects.create(
            startup=startup,
            party_name=party_name,
            file=file
        )
        messages.success(request, f'NDA with "{party_name}" created successfully!')
        return redirect('legal:nda')
    
    context = {
        'page_title': 'Add NDA',
        'page_icon': '🔒',
        'page_subtitle': 'Upload a new Non-Disclosure Agreement',
        'is_edit': False,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/nda_form.html', context)

@login_required
def nda_delete(request, pk):
    """Delete an NDA."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    nda = get_object_or_404(NDA, pk=pk, startup=startup)
    
    if request.method == 'POST':
        party_name = nda.party_name
        nda.delete()
        messages.success(request, f'NDA with "{party_name}" deleted successfully!')
        return redirect('legal:nda')
    
    context = {
        'nda': nda,
        'page_title': 'Delete NDA',
        'page_icon': '🗑️',
        'page_subtitle': 'Confirm deletion of NDA',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/nda_confirm_delete.html', context)

@login_required
def nda_toggle_signed(request, pk):
    """Toggle NDA signed status."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    nda = get_object_or_404(NDA, pk=pk, startup=startup)
    nda.signed = not nda.signed
    nda.save()
    
    status = "signed" if nda.signed else "marked as unsigned"
    messages.success(request, f'NDA with "{nda.party_name}" {status} successfully!')
    return redirect('legal:nda')

# ============================================
# VENDOR AGREEMENTS
# ============================================

@login_required
def vendor_agreements(request):
    """List all vendor agreements."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    vendors = VendorAgreement.objects.filter(startup=startup).order_by('vendor_name')
    
    context = {
        'vendors': vendors,
        'page_title': 'Vendor Agreements',
        'page_icon': '🤝',
        'page_subtitle': 'Manage vendor agreements',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/vendor_agreements.html', context)

@login_required
def vendor_agreement_create(request):
    """Create a new vendor agreement."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    if request.method == 'POST':
        vendor_name = request.POST.get('vendor_name')
        file = request.FILES.get('file')
        
        if not all([vendor_name, file]):
            messages.error(request, 'All fields are required.')
            return redirect('legal:vendor_agreement_create')
        
        VendorAgreement.objects.create(
            startup=startup,
            vendor_name=vendor_name,
            file=file
        )
        messages.success(request, f'Vendor agreement for "{vendor_name}" created successfully!')
        return redirect('legal:vendor_agreements')
    
    context = {
        'page_title': 'Add Vendor Agreement',
        'page_icon': '🤝',
        'page_subtitle': 'Upload a new vendor agreement',
        'is_edit': False,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/vendor_agreement_form.html', context)

@login_required
def vendor_agreement_delete(request, pk):
    """Delete a vendor agreement."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    vendor = get_object_or_404(VendorAgreement, pk=pk, startup=startup)
    
    if request.method == 'POST':
        vendor_name = vendor.vendor_name
        vendor.delete()
        messages.success(request, f'Vendor agreement for "{vendor_name}" deleted successfully!')
        return redirect('legal:vendor_agreements')
    
    context = {
        'vendor': vendor,
        'page_title': 'Delete Vendor Agreement',
        'page_icon': '🗑️',
        'page_subtitle': 'Confirm deletion of vendor agreement',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/vendor_agreement_confirm_delete.html', context)

@login_required
def vendor_agreement_toggle_active(request, pk):
    """Toggle vendor agreement active status."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    vendor = get_object_or_404(VendorAgreement, pk=pk, startup=startup)
    vendor.active = not vendor.active
    vendor.save()
    
    status = "activated" if vendor.active else "deactivated"
    messages.success(request, f'Vendor agreement for "{vendor.vendor_name}" {status} successfully!')
    return redirect('legal:vendor_agreements')

# ============================================
# CLIENT AGREEMENTS
# ============================================

@login_required
def client_agreements(request):
    """List all client agreements."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    clients = ClientAgreement.objects.filter(startup=startup).order_by('client_name')
    total_value = clients.aggregate(Sum('value'))['value__sum'] or 0
    
    context = {
        'clients': clients,
        'total_value': total_value,
        'page_title': 'Client Agreements',
        'page_icon': '🤝',
        'page_subtitle': 'Manage client agreements',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/client_agreements.html', context)

@login_required
def client_agreement_create(request):
    """Create a new client agreement."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    if request.method == 'POST':
        client_name = request.POST.get('client_name')
        value = request.POST.get('value')
        file = request.FILES.get('file')
        
        if not all([client_name, value, file]):
            messages.error(request, 'All fields are required.')
            return redirect('legal:client_agreement_create')
        
        ClientAgreement.objects.create(
            startup=startup,
            client_name=client_name,
            value=value,
            file=file
        )
        messages.success(request, f'Client agreement for "{client_name}" created successfully!')
        return redirect('legal:client_agreements')
    
    context = {
        'page_title': 'Add Client Agreement',
        'page_icon': '🤝',
        'page_subtitle': 'Upload a new client agreement',
        'is_edit': False,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/client_agreement_form.html', context)

@login_required
def client_agreement_delete(request, pk):
    """Delete a client agreement."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    client = get_object_or_404(ClientAgreement, pk=pk, startup=startup)
    
    if request.method == 'POST':
        client_name = client.client_name
        client.delete()
        messages.success(request, f'Client agreement for "{client_name}" deleted successfully!')
        return redirect('legal:client_agreements')
    
    context = {
        'client': client,
        'page_title': 'Delete Client Agreement',
        'page_icon': '🗑️',
        'page_subtitle': 'Confirm deletion of client agreement',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/client_agreement_confirm_delete.html', context)

# ============================================
# TRADEMARKS
# ============================================

@login_required
def trademarks(request):
    """List all trademarks."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    trademarks = Trademark.objects.filter(startup=startup).order_by('trademark_name')
    
    context = {
        'trademarks': trademarks,
        'page_title': 'Trademarks',
        'page_icon': '™️',
        'page_subtitle': 'Manage trademarks',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/trademarks.html', context)

@login_required
def trademark_create(request):
    """Create a new trademark."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    if request.method == 'POST':
        trademark_name = request.POST.get('trademark_name')
        status = request.POST.get('status')
        application_number = request.POST.get('application_number')
        
        if not all([trademark_name, status, application_number]):
            messages.error(request, 'All fields are required.')
            return redirect('legal:trademark_create')
        
        Trademark.objects.create(
            startup=startup,
            trademark_name=trademark_name,
            status=status,
            application_number=application_number
        )
        messages.success(request, f'Trademark "{trademark_name}" created successfully!')
        return redirect('legal:trademarks')
    
    context = {
        'page_title': 'Add Trademark',
        'page_icon': '™️',
        'page_subtitle': 'Register a new trademark',
        'is_edit': False,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/trademark_form.html', context)

@login_required
def trademark_edit(request, pk):
    """Edit a trademark."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    trademark = get_object_or_404(Trademark, pk=pk, startup=startup)
    
    if request.method == 'POST':
        trademark.trademark_name = request.POST.get('trademark_name')
        trademark.status = request.POST.get('status')
        trademark.application_number = request.POST.get('application_number')
        trademark.save()
        messages.success(request, f'Trademark "{trademark.trademark_name}" updated successfully!')
        return redirect('legal:trademarks')
    
    context = {
        'trademark': trademark,
        'page_title': 'Edit Trademark',
        'page_icon': '✏️',
        'page_subtitle': 'Update trademark details',
        'is_edit': True,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/trademark_form.html', context)

@login_required
def trademark_delete(request, pk):
    """Delete a trademark."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    trademark = get_object_or_404(Trademark, pk=pk, startup=startup)
    
    if request.method == 'POST':
        trademark_name = trademark.trademark_name
        trademark.delete()
        messages.success(request, f'Trademark "{trademark_name}" deleted successfully!')
        return redirect('legal:trademarks')
    
    context = {
        'trademark': trademark,
        'page_title': 'Delete Trademark',
        'page_icon': '🗑️',
        'page_subtitle': 'Confirm deletion of trademark',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/trademark_confirm_delete.html', context)

# ============================================
# IP ASSIGNMENTS
# ============================================

@login_required
def ip_assignments(request):
    """List all IP assignments."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    ip_assignments = IPAssignment.objects.filter(startup=startup).order_by('contributor')
    
    context = {
        'ip_assignments': ip_assignments,
        'page_title': 'IP Assignments',
        'page_icon': '💡',
        'page_subtitle': 'Manage intellectual property assignments',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/ip_assignments.html', context)

@login_required
def ip_assignment_create(request):
    """Create a new IP assignment."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    if request.method == 'POST':
        contributor = request.POST.get('contributor')
        document = request.FILES.get('document')
        
        if not all([contributor, document]):
            messages.error(request, 'All fields are required.')
            return redirect('legal:ip_assignment_create')
        
        IPAssignment.objects.create(
            startup=startup,
            contributor=contributor,
            document=document
        )
        messages.success(request, f'IP assignment for "{contributor}" created successfully!')
        return redirect('legal:ip_assignments')
    
    context = {
        'page_title': 'Add IP Assignment',
        'page_icon': '💡',
        'page_subtitle': 'Upload a new IP assignment document',
        'is_edit': False,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/ip_assignment_form.html', context)

@login_required
def ip_assignment_delete(request, pk):
    """Delete an IP assignment."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    ip_assignment = get_object_or_404(IPAssignment, pk=pk, startup=startup)
    
    if request.method == 'POST':
        contributor = ip_assignment.contributor
        ip_assignment.delete()
        messages.success(request, f'IP assignment for "{contributor}" deleted successfully!')
        return redirect('legal:ip_assignments')
    
    context = {
        'ip_assignment': ip_assignment,
        'page_title': 'Delete IP Assignment',
        'page_icon': '🗑️',
        'page_subtitle': 'Confirm deletion of IP assignment',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/ip_assignment_confirm_delete.html', context)

# ============================================
# SHAREHOLDER AGREEMENTS
# ============================================

@login_required
def shareholders(request):
    """List all shareholder agreements."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    shareholders = ShareholderAgreement.objects.filter(startup=startup).order_by('-created_at')
    
    context = {
        'shareholders': shareholders,
        'page_title': 'Shareholder Agreements',
        'page_icon': '📊',
        'page_subtitle': 'Manage shareholder agreements',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/shareholders.html', context)

@login_required
def shareholder_agreement_create(request):
    """Create a new shareholder agreement."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    if request.method == 'POST':
        document = request.FILES.get('document')
        
        if not document:
            messages.error(request, 'Document is required.')
            return redirect('legal:shareholder_agreement_create')
        
        ShareholderAgreement.objects.create(
            startup=startup,
            document=document
        )
        messages.success(request, 'Shareholder agreement created successfully!')
        return redirect('legal:shareholders')
    
    context = {
        'page_title': 'Add Shareholder Agreement',
        'page_icon': '📊',
        'page_subtitle': 'Upload a new shareholder agreement',
        'is_edit': False,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/shareholder_agreement_form.html', context)

@login_required
def shareholder_agreement_delete(request, pk):
    """Delete a shareholder agreement."""
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('legal:legal_dashboard')
    
    shareholder = get_object_or_404(ShareholderAgreement, pk=pk, startup=startup)
    
    if request.method == 'POST':
        shareholder.delete()
        messages.success(request, 'Shareholder agreement deleted successfully!')
        return redirect('legal:shareholders')
    
    context = {
        'shareholder': shareholder,
        'page_title': 'Delete Shareholder Agreement',
        'page_icon': '🗑️',
        'page_subtitle': 'Confirm deletion of shareholder agreement',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'legal/shareholder_agreement_confirm_delete.html', context)