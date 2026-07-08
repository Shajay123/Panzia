# finance/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    Income, Expense, Invoice, Receivable, 
    Vendor, AccountsPayable, Reimbursement
)
from startups.models import StartupProfile
from people.models import Employee


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_user_startup(request):
    """Get the startup associated with the current user."""
    try:
        if hasattr(request.user, 'startup') and request.user.startup:
            return request.user.startup
        
        if hasattr(request.user, 'startup_profile') and request.user.startup_profile:
            return request.user.startup_profile
        
        try:
            employee = Employee.objects.get(user=request.user)
            if employee.startup:
                return employee.startup
        except Employee.DoesNotExist:
            pass
        
        try:
            startup_profile = StartupProfile.objects.get(user=request.user)
            return startup_profile
        except StartupProfile.DoesNotExist:
            pass
        
        return None
    except Exception as e:
        print(f"Error getting startup: {e}")
        return None


def check_hr_access(request):
    """Check if user has HR access (HR, Admin, or Superuser)."""
    if request.user.is_superuser:
        return True
    
    if hasattr(request.user, 'role'):
        if request.user.role in ['hr', 'startup_hr', 'admin', 'startup_admin']:
            return True
    
    try:
        employee = Employee.objects.get(user=request.user)
        if employee.role in ['hr', 'startup_hr', 'admin', 'startup_admin']:
            return True
    except Employee.DoesNotExist:
        pass
    
    return False


def check_finance_access(request):
    """Check if user has finance access."""
    return check_hr_access(request)


# ============================================
# DASHBOARD
# ============================================

# finance/views.py - Updated finance_dashboard

@login_required
def finance_dashboard(request):
    """Finance Dashboard - Overview of all financial data."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile. Please contact your HR.')
        context = {
            'startup': None,
            'total_income': 0,
            'monthly_income': 0,
            'total_expenses': 0,
            'monthly_expenses': 0,
            'total_profit': 0,
            'monthly_profit': 0,
            'total_invoices': 0,
            'paid_invoices': 0,
            'overdue_invoices': 0,
            'total_receivable': 0,
            'total_receivable_paid': 0,
            'total_receivable_all': 0,  # Added for total including paid
            'receivable_due_count': 0,
            'receivable_paid_count': 0,
            'receivable_total_count': 0,
            'total_payable': 0,
            'total_payable_paid': 0,
            'total_payable_all': 0,  # Added for total including paid
            'payable_due_count': 0,
            'payable_paid_count': 0,
            'payable_total_count': 0,
            'expenses_by_category': [],
            'recent_incomes': [],
            'recent_expenses': [],
            'recent_invoices': [],
            'all_incomes': [],
            'page_title': 'Finance Dashboard',
            'page_icon': '💰',
            'page_subtitle': 'Overview of your startup\'s financial health',
            'is_hr': check_hr_access(request),
            'no_startup': True,
        }
        return render(request, 'finance/dashboard.html', context)
    
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    # ===== INCOME =====
    total_income = Income.objects.filter(startup=startup).aggregate(Sum('amount'))['amount__sum'] or 0
    
    monthly_income = Income.objects.filter(
        startup=startup,
        received_date__month=current_month,
        received_date__year=current_year
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # ===== ALL INCOMES (for dashboard list) =====
    all_incomes = Income.objects.filter(startup=startup).order_by('-received_date')[:10]
    
    # ===== EXPENSES =====
    total_expenses = Expense.objects.filter(startup=startup).aggregate(Sum('amount'))['amount__sum'] or 0
    
    monthly_expenses = Expense.objects.filter(
        startup=startup,
        expense_date__month=current_month,
        expense_date__year=current_year
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # ===== PROFIT =====
    total_profit = total_income - total_expenses
    monthly_profit = monthly_income - monthly_expenses
    
    # ===== INVOICES =====
    total_invoices = Invoice.objects.filter(startup=startup).count()
    paid_invoices = Invoice.objects.filter(startup=startup, status='Paid').count()
    overdue_invoices = Invoice.objects.filter(startup=startup, status='Overdue').count()
    
    # ===== RECEIVABLE =====
    # Get all receivables for this startup
    all_receivables = Receivable.objects.filter(invoice__startup=startup)
    
    # Total receivable amount (unpaid only)
    total_receivable = all_receivables.filter(paid=False).aggregate(Sum('amount_due'))['amount_due__sum'] or 0
    
    # Total receivable amount (paid only)
    total_receivable_paid = all_receivables.filter(paid=True).aggregate(Sum('amount_due'))['amount_due__sum'] or 0
    
    # Total receivable amount (ALL including paid) - This will show the full amount
    total_receivable_all = all_receivables.aggregate(Sum('amount_due'))['amount_due__sum'] or 0
    
    # Counts
    receivable_total_count = all_receivables.count()
    receivable_due_count = all_receivables.filter(paid=False).count()
    receivable_paid_count = all_receivables.filter(paid=True).count()
    
    # ===== PAYABLE =====
    # Get all payables for this startup
    all_payables = AccountsPayable.objects.filter(vendor__startup=startup)
    
    # Total payable amount (unpaid only)
    total_payable = all_payables.filter(paid=False).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Total payable amount (paid only)
    total_payable_paid = all_payables.filter(paid=True).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Total payable amount (ALL including paid) - This will show the full amount
    total_payable_all = all_payables.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Counts
    payable_total_count = all_payables.count()
    payable_due_count = all_payables.filter(paid=False).count()
    payable_paid_count = all_payables.filter(paid=True).count()
    
    # Debug prints to verify data
    print(f"=== DASHBOARD DEBUG ===")
    print(f"Receivable - Unpaid: {total_receivable}, Paid: {total_receivable_paid}, All: {total_receivable_all}")
    print(f"Payable - Unpaid: {total_payable}, Paid: {total_payable_paid}, All: {total_payable_all}")
    
    # ===== EXPENSES BY CATEGORY =====
    expenses_by_category = Expense.objects.filter(
        startup=startup,
        expense_date__month=current_month,
        expense_date__year=current_year
    ).values('category').annotate(total=Sum('amount')).order_by('-total')
    
    # Calculate percentage for each category and add color
    for category in expenses_by_category:
        if monthly_expenses > 0:
            category['percentage'] = (category['total'] / monthly_expenses) * 100
        else:
            category['percentage'] = 0
        
        # Add color based on category name
        category_colors = {
            'Salary': '#f87171',
            'Software': '#60a5fa',
            'Marketing': '#fbbf24',
            'Office': '#a78bfa',
            'Travel': '#f472b6',
            'Other': '#94a3b8',
        }
        category['color'] = category_colors.get(category['category'], '#94a3b8')
    
    # ===== RECENT TRANSACTIONS =====
    recent_incomes = Income.objects.filter(startup=startup).order_by('-received_date')[:5]
    recent_expenses = Expense.objects.filter(startup=startup).order_by('-expense_date')[:5]
    recent_invoices = Invoice.objects.filter(startup=startup).order_by('-created_at')[:5]
    
    # ===== MONTH NAME =====
    month_name = today.strftime('%B')
    
    context = {
        'startup': startup,
        # Income
        'total_income': total_income,
        'monthly_income': monthly_income,
        'all_incomes': all_incomes,
        # Expenses
        'total_expenses': total_expenses,
        'monthly_expenses': monthly_expenses,
        'expenses_by_category': expenses_by_category,
        # Profit
        'total_profit': total_profit,
        'monthly_profit': monthly_profit,
        # Invoices
        'total_invoices': total_invoices,
        'paid_invoices': paid_invoices,
        'overdue_invoices': overdue_invoices,
        # Receivable - Full data
        'total_receivable': total_receivable_all,  # Show ALL including paid
        'total_receivable_unpaid': total_receivable,  # Keep unpaid separately
        'total_receivable_paid': total_receivable_paid,
        'receivable_total_count': receivable_total_count,
        'receivable_due_count': receivable_due_count,
        'receivable_paid_count': receivable_paid_count,
        # Payable - Full data
        'total_payable': total_payable_all,  # Show ALL including paid
        'total_payable_unpaid': total_payable,  # Keep unpaid separately
        'total_payable_paid': total_payable_paid,
        'payable_total_count': payable_total_count,
        'payable_due_count': payable_due_count,
        'payable_paid_count': payable_paid_count,
        # Recent
        'recent_incomes': recent_incomes,
        'recent_expenses': recent_expenses,
        'recent_invoices': recent_invoices,
        # Filter
        'selected_month': 'all',
        'month_name': month_name,
        # Page
        'page_title': 'Finance Dashboard',
        'page_icon': '💰',
        'page_subtitle': 'Overview of your startup\'s financial health',
        'is_hr': check_hr_access(request),
        'no_startup': False,
    }
    return render(request, 'finance/dashboard.html', context)

# ============================================
# INCOME VIEWS
# ============================================

@login_required
def income_list(request):
    """List all income entries."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile. Please contact your HR.')
        context = {
            'incomes': [],
            'total_amount': 0,
            'total_expenses': 0,
            'monthly_income': 0,
            'monthly_expenses': 0,
            'net_profit': 0,
            'monthly_profit': 0,
            'total_income_count': 0,
            'page_title': 'Income',
            'page_icon': '💵',
            'page_subtitle': 'Manage your income entries',
            'is_hr': check_hr_access(request),
            'no_startup': True,
        }
        return render(request, 'finance/income_list.html', context)
    
    # Get all incomes
    incomes = Income.objects.filter(startup=startup).order_by('-received_date')
    
    # Apply filters
    search = request.GET.get('search')
    if search:
        incomes = incomes.filter(Q(title__icontains=search) | Q(client__icontains=search))
    
    date_from = request.GET.get('date_from')
    if date_from:
        incomes = incomes.filter(received_date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        incomes = incomes.filter(received_date__lte=date_to)
    
    # Calculate totals
    total_amount = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    total_income_count = incomes.count()
    
    # Get current month data
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year
    
    monthly_income = Income.objects.filter(
        startup=startup,
        received_date__month=current_month,
        received_date__year=current_year
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Get total expenses (for the overview card)
    total_expenses = Expense.objects.filter(startup=startup).aggregate(Sum('amount'))['amount__sum'] or 0
    
    monthly_expenses = Expense.objects.filter(
        startup=startup,
        expense_date__month=current_month,
        expense_date__year=current_year
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Calculate profits
    net_profit = total_amount - total_expenses
    monthly_profit = monthly_income - monthly_expenses
    
    context = {
        'incomes': incomes,
        'total_amount': total_amount,
        'total_expenses': total_expenses,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'net_profit': net_profit,
        'monthly_profit': monthly_profit,
        'total_income_count': total_income_count,
        'page_title': 'Income',
        'page_icon': '💵',
        'page_subtitle': 'Manage your income entries',
        'is_hr': check_hr_access(request),
        'no_startup': False,
    }
    return render(request, 'finance/income_list.html', context)


@login_required
def income_create(request):
    """Create a new income entry."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('finance:finance_dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        client = request.POST.get('client')
        amount = request.POST.get('amount')
        received_date = request.POST.get('received_date')
        
        if not all([title, client, amount, received_date]):
            messages.error(request, 'All fields are required.')
            return redirect('finance:income_create')
        
        Income.objects.create(
            startup=startup,
            title=title,
            client=client,
            amount=amount,
            received_date=received_date
        )
        messages.success(request, f'Income "{title}" created successfully!')
        return redirect('finance:income_list')
    
    context = {
        'page_title': 'Add Income',
        'page_icon': '💵',
        'page_subtitle': 'Record a new income entry',
        'is_edit': False,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'finance/income_form.html', context)


@login_required
def income_edit(request, pk):
    """Edit an income entry."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('finance:finance_dashboard')
    
    income = get_object_or_404(Income, pk=pk, startup=startup)
    
    if request.method == 'POST':
        income.title = request.POST.get('title')
        income.client = request.POST.get('client')
        income.amount = request.POST.get('amount')
        income.received_date = request.POST.get('received_date')
        income.save()
        messages.success(request, 'Income updated successfully!')
        return redirect('finance:income_list')
    
    context = {
        'income': income,
        'page_title': 'Edit Income',
        'page_icon': '✏️',
        'page_subtitle': 'Update income details',
        'is_edit': True,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'finance/income_form.html', context)


@login_required
def income_delete(request, pk):
    """Delete an income entry."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('finance:finance_dashboard')
    
    income = get_object_or_404(Income, pk=pk, startup=startup)
    
    if request.method == 'POST':
        title = income.title
        income.delete()
        messages.success(request, f'Income "{title}" deleted successfully!')
        return redirect('finance:income_list')
    
    context = {
        'income': income,
        'page_title': 'Delete Income',
        'page_icon': '🗑️',
        'page_subtitle': 'Confirm deletion of income entry',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'finance/income_confirm_delete.html', context)


# ============================================
# EXPENSE VIEWS
# ============================================

@login_required
def expense_list(request):
    """List all expense entries."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile. Please contact your HR.')
        context = {
            'expenses': [],
            'total_amount': 0,
            'categories': Expense.CATEGORY,
            'page_title': 'Expenses',
            'page_icon': '💸',
            'page_subtitle': 'Manage your expense entries',
            'is_hr': check_hr_access(request),
            'no_startup': True,
        }
        return render(request, 'finance/expense_list.html', context)
    
    expenses = Expense.objects.filter(startup=startup).order_by('-expense_date')
    
    search = request.GET.get('search')
    if search:
        expenses = expenses.filter(title__icontains=search)
    
    category = request.GET.get('category')
    if category:
        expenses = expenses.filter(category=category)
    
    date_from = request.GET.get('date_from')
    if date_from:
        expenses = expenses.filter(expense_date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        expenses = expenses.filter(expense_date__lte=date_to)
    
    total_amount = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'expenses': expenses,
        'total_amount': total_amount,
        'categories': Expense.CATEGORY,
        'page_title': 'Expenses',
        'page_icon': '💸',
        'page_subtitle': 'Manage your expense entries',
        'is_hr': check_hr_access(request),
        'no_startup': False,
    }
    return render(request, 'finance/expense_list.html', context)


# ============================================
# EXPENSE CREATE, EDIT, DELETE
# ============================================

@login_required
def expense_create(request):
    """Create a new expense entry."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('finance:finance_dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('category')
        amount = request.POST.get('amount')
        expense_date = request.POST.get('expense_date')
        
        if not all([title, category, amount, expense_date]):
            messages.error(request, 'All fields are required.')
            return redirect('finance:expense_create')
        
        Expense.objects.create(
            startup=startup,
            title=title,
            category=category,
            amount=amount,
            expense_date=expense_date
        )
        messages.success(request, f'Expense "{title}" created successfully!')
        return redirect('finance:expense_list')
    
    context = {
        'categories': Expense.CATEGORY,
        'page_title': 'Add Expense',
        'page_icon': '💸',
        'page_subtitle': 'Record a new expense entry',
        'is_edit': False,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'finance/expense_form.html', context)


@login_required
def expense_edit(request, pk):
    """Edit an expense entry."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('finance:finance_dashboard')
    
    expense = get_object_or_404(Expense, pk=pk, startup=startup)
    
    if request.method == 'POST':
        expense.title = request.POST.get('title')
        expense.category = request.POST.get('category')
        expense.amount = request.POST.get('amount')
        expense.expense_date = request.POST.get('expense_date')
        expense.save()
        messages.success(request, 'Expense updated successfully!')
        return redirect('finance:expense_list')
    
    context = {
        'expense': expense,
        'categories': Expense.CATEGORY,
        'page_title': 'Edit Expense',
        'page_icon': '✏️',
        'page_subtitle': 'Update expense details',
        'is_edit': True,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'finance/expense_form.html', context)


@login_required
def expense_delete(request, pk):
    """Delete an expense entry."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('finance:finance_dashboard')
    
    expense = get_object_or_404(Expense, pk=pk, startup=startup)
    
    if request.method == 'POST':
        title = expense.title
        expense.delete()
        messages.success(request, f'Expense "{title}" deleted successfully!')
        return redirect('finance:expense_list')
    
    context = {
        'expense': expense,
        'page_title': 'Delete Expense',
        'page_icon': '🗑️',
        'page_subtitle': 'Confirm deletion of expense entry',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'finance/expense_confirm_delete.html', context)


# ============================================
# INVOICE VIEWS
# ============================================

@login_required
def invoice_list(request):
    """List all invoices."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile. Please contact your HR.')
        context = {
            'invoices': [],
            'total_amount': 0,
            'total_paid': 0,
            'total_due': 0,
            'statuses': Invoice.STATUS,
            'page_title': 'Invoices',
            'page_icon': '🧾',
            'page_subtitle': 'Manage your invoices',
            'is_hr': check_hr_access(request),
            'no_startup': True,
        }
        return render(request, 'finance/invoice_list.html', context)
    
    invoices = Invoice.objects.filter(startup=startup).order_by('-created_at')
    
    status = request.GET.get('status')
    if status:
        invoices = invoices.filter(status=status)
    
    search = request.GET.get('search')
    if search:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search) | 
            Q(client_name__icontains=search)
        )
    
    total_amount = invoices.aggregate(Sum('amount'))['amount__sum'] or 0
    total_paid = invoices.filter(status='Paid').aggregate(Sum('amount'))['amount__sum'] or 0
    total_due = invoices.filter(status__in=['Sent', 'Overdue', 'Draft']).aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'invoices': invoices,
        'total_amount': total_amount,
        'total_paid': total_paid,
        'total_due': total_due,
        'statuses': Invoice.STATUS,
        'page_title': 'Invoices',
        'page_icon': '🧾',
        'page_subtitle': 'Manage your invoices',
        'is_hr': check_hr_access(request),
        'no_startup': False,
    }
    return render(request, 'finance/invoice_list.html', context)


@login_required
def invoice_create(request):
    """Create a new invoice."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('finance:finance_dashboard')
    
    if request.method == 'POST':
        client_name = request.POST.get('client_name')
        amount = request.POST.get('amount')
        due_date = request.POST.get('due_date')
        status = request.POST.get('status', 'Draft')
        
        if not all([client_name, amount, due_date]):
            messages.error(request, 'All fields are required.')
            return redirect('finance:invoice_create')
        
        # Generate invoice number
        last_invoice = Invoice.objects.filter(startup=startup).order_by('-id').first()
        if last_invoice:
            try:
                last_num = int(last_invoice.invoice_number.split('-')[-1])
                next_num = last_num + 1
            except:
                next_num = 1
        else:
            next_num = 1
        
        invoice_number = f"INV-{timezone.now().year}-{str(next_num).zfill(4)}"
        
        invoice = Invoice.objects.create(
            startup=startup,
            invoice_number=invoice_number,
            client_name=client_name,
            amount=amount,
            due_date=due_date,
            status=status
        )
        
        # Create receivable entry
        Receivable.objects.create(
            invoice=invoice,
            amount_due=amount,
            paid=(status == 'Paid')
        )
        
        messages.success(request, f'Invoice "{invoice_number}" created successfully!')
        return redirect('finance:invoice_list')
    
    context = {
        'statuses': Invoice.STATUS,
        'page_title': 'Create Invoice',
        'page_icon': '🧾',
        'page_subtitle': 'Create a new invoice',
        'is_edit': False,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'finance/invoice_create.html', context)


@login_required
def invoice_detail(request, pk):
    """View invoice details."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('finance:finance_dashboard')
    
    invoice = get_object_or_404(Invoice, pk=pk, startup=startup)
    receivable = Receivable.objects.filter(invoice=invoice).first()
    
    context = {
        'invoice': invoice,
        'receivable': receivable,
        'page_title': f'Invoice {invoice.invoice_number}',
        'page_icon': '🧾',
        'page_subtitle': 'View invoice details',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'finance/invoice_detail.html', context)


@login_required
def invoice_edit(request, pk):
    """Edit an invoice."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('finance:finance_dashboard')
    
    invoice = get_object_or_404(Invoice, pk=pk, startup=startup)
    
    if request.method == 'POST':
        invoice.client_name = request.POST.get('client_name')
        invoice.amount = request.POST.get('amount')
        invoice.due_date = request.POST.get('due_date')
        invoice.status = request.POST.get('status')
        invoice.save()
        messages.success(request, 'Invoice updated successfully!')
        return redirect('finance:invoice_list')
    
    context = {
        'invoice': invoice,
        'statuses': Invoice.STATUS,
        'page_title': 'Edit Invoice',
        'page_icon': '✏️',
        'page_subtitle': 'Update invoice details',
        'is_edit': True,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'finance/invoice_create.html', context)


@login_required
def invoice_delete(request, pk):
    """Delete an invoice."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('finance:finance_dashboard')
    
    invoice = get_object_or_404(Invoice, pk=pk, startup=startup)
    
    if request.method == 'POST':
        invoice_number = invoice.invoice_number
        invoice.delete()
        messages.success(request, f'Invoice "{invoice_number}" deleted successfully!')
        return redirect('finance:invoice_list')
    
    context = {
        'invoice': invoice,
        'page_title': 'Delete Invoice',
        'page_icon': '🗑️',
        'page_subtitle': 'Confirm deletion of invoice',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'finance/invoice_confirm_delete.html', context)


# ============================================
# RECEIVABLE VIEWS
# ============================================

@login_required
def receivable_list(request):
    """List all accounts receivable."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        context = {
            'receivables': [],
            'total_due': 0,
            'total_paid': 0,
            'page_title': 'Accounts Receivable',
            'page_icon': '📥',
            'page_subtitle': 'Track your accounts receivable',
            'is_hr': check_hr_access(request),
            'no_startup': True,
        }
        return render(request, 'finance/receivable_list.html', context)
    
    receivables = Receivable.objects.filter(
        invoice__startup=startup
    ).select_related('invoice').order_by('invoice__due_date')
    
    total_due = receivables.filter(paid=False).aggregate(Sum('amount_due'))['amount_due__sum'] or 0
    total_paid = receivables.filter(paid=True).aggregate(Sum('amount_due'))['amount_due__sum'] or 0
    
    context = {
        'receivables': receivables,
        'total_due': total_due,
        'total_paid': total_paid,
        'page_title': 'Accounts Receivable',
        'page_icon': '📥',
        'page_subtitle': 'Track your accounts receivable',
        'is_hr': check_hr_access(request),
        'no_startup': False,
    }
    return render(request, 'finance/receivable_list.html', context)


@login_required
def receivable_mark_paid(request, pk):
    """Mark receivable as paid."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('finance:finance_dashboard')
    
    receivable = get_object_or_404(Receivable, pk=pk, invoice__startup=startup)
    
    if request.method == 'POST':
        receivable.paid = True
        receivable.save()
        
        # Update invoice status
        invoice = receivable.invoice
        if invoice.status != 'Paid':
            invoice.status = 'Paid'
            invoice.save()
        
        messages.success(request, 'Receivable marked as paid!')
        return redirect('finance:receivable_list')
    
    context = {
        'receivable': receivable,
        'page_title': 'Mark as Paid',
        'page_icon': '✅',
        'page_subtitle': 'Confirm payment of receivable',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'finance/receivable_mark_paid.html', context)


# ============================================
# VENDOR VIEWS
# ============================================

@login_required
def vendor_list(request):
    """List all vendors."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        context = {
            'vendors': [],
            'page_title': 'Vendors',
            'page_icon': '🏢',
            'page_subtitle': 'Manage your vendors',
            'is_hr': check_hr_access(request),
            'no_startup': True,
        }
        return render(request, 'finance/vendor_list.html', context)
    
    vendors = Vendor.objects.filter(startup=startup).order_by('vendor_name')
    
    search = request.GET.get('search')
    if search:
        vendors = vendors.filter(vendor_name__icontains=search)
    
    context = {
        'vendors': vendors,
        'page_title': 'Vendors',
        'page_icon': '🏢',
        'page_subtitle': 'Manage your vendors',
        'is_hr': check_hr_access(request),
        'no_startup': False,
    }
    return render(request, 'finance/vendor_list.html', context)


@login_required
def vendor_create(request):
    """Create a new vendor."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('finance:finance_dashboard')
    
    if request.method == 'POST':
        vendor_name = request.POST.get('vendor_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        
        if not all([vendor_name, phone, email]):
            messages.error(request, 'All fields are required.')
            return redirect('finance:vendor_create')
        
        Vendor.objects.create(
            startup=startup,
            vendor_name=vendor_name,
            phone=phone,
            email=email
        )
        messages.success(request, f'Vendor "{vendor_name}" created successfully!')
        return redirect('finance:vendor_list')
    
    context = {
        'page_title': 'Add Vendor',
        'page_icon': '🏢',
        'page_subtitle': 'Add a new vendor',
        'is_edit': False,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'finance/vendor_form.html', context)


@login_required
def vendor_edit(request, pk):
    """Edit a vendor."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('finance:finance_dashboard')
    
    vendor = get_object_or_404(Vendor, pk=pk, startup=startup)
    
    if request.method == 'POST':
        vendor.vendor_name = request.POST.get('vendor_name')
        vendor.phone = request.POST.get('phone')
        vendor.email = request.POST.get('email')
        vendor.save()
        messages.success(request, 'Vendor updated successfully!')
        return redirect('finance:vendor_list')
    
    context = {
        'vendor': vendor,
        'page_title': 'Edit Vendor',
        'page_icon': '✏️',
        'page_subtitle': 'Update vendor details',
        'is_edit': True,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'finance/vendor_form.html', context)


@login_required
def vendor_delete(request, pk):
    """Delete a vendor."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('finance:finance_dashboard')
    
    vendor = get_object_or_404(Vendor, pk=pk, startup=startup)
    
    if request.method == 'POST':
        vendor_name = vendor.vendor_name
        vendor.delete()
        messages.success(request, f'Vendor "{vendor_name}" deleted successfully!')
        return redirect('finance:vendor_list')
    
    context = {
        'vendor': vendor,
        'page_title': 'Delete Vendor',
        'page_icon': '🗑️',
        'page_subtitle': 'Confirm deletion of vendor',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'finance/vendor_confirm_delete.html', context)


# ============================================
# PAYABLE VIEWS
# ============================================

@login_required
def payable_list(request):
    """List all accounts payable."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        context = {
            'payables': [],
            'total_due': 0,
            'total_paid': 0,
            'due_count': 0,
            'paid_count': 0,
            'total_payable_count': 0,
            'page_title': 'Accounts Payable',
            'page_icon': '📤',
            'page_subtitle': 'Manage your accounts payable',
            'is_hr': check_hr_access(request),
            'no_startup': True,
        }
        return render(request, 'finance/payable_list.html', context)
    
    payables = AccountsPayable.objects.filter(
        vendor__startup=startup
    ).select_related('vendor').order_by('due_date')
    
    total_due = payables.filter(paid=False).aggregate(Sum('amount'))['amount__sum'] or 0
    total_paid = payables.filter(paid=True).aggregate(Sum('amount'))['amount__sum'] or 0
    due_count = payables.filter(paid=False).count()
    paid_count = payables.filter(paid=True).count()
    total_payable_count = payables.count()
    
    context = {
        'payables': payables,
        'total_due': total_due,
        'total_paid': total_paid,
        'due_count': due_count,
        'paid_count': paid_count,
        'total_payable_count': total_payable_count,
        'page_title': 'Accounts Payable',
        'page_icon': '📤',
        'page_subtitle': 'Manage your accounts payable',
        'is_hr': check_hr_access(request),
        'no_startup': False,
    }
    return render(request, 'finance/payable_list.html', context)

@login_required
def payable_create(request):
    """Create a new accounts payable entry."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('finance:finance_dashboard')
    
    vendors = Vendor.objects.filter(startup=startup)
    
    if request.method == 'POST':
        vendor_id = request.POST.get('vendor')
        amount = request.POST.get('amount')
        due_date = request.POST.get('due_date')
        
        if not all([vendor_id, amount, due_date]):
            messages.error(request, 'All fields are required.')
            return redirect('finance:payable_create')
        
        vendor = get_object_or_404(Vendor, pk=vendor_id, startup=startup)
        
        AccountsPayable.objects.create(
            vendor=vendor,
            amount=amount,
            due_date=due_date
        )
        messages.success(request, f'Payable for "{vendor.vendor_name}" created successfully!')
        return redirect('finance:payable_list')
    
    context = {
        'vendors': vendors,
        'page_title': 'Add Accounts Payable',
        'page_icon': '📤',
        'page_subtitle': 'Add a new accounts payable entry',
        'is_edit': False,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'finance/payable_form.html', context)


@login_required
def payable_edit(request, pk):
    """Edit an accounts payable entry."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('finance:finance_dashboard')
    
    payable = get_object_or_404(AccountsPayable, pk=pk, vendor__startup=startup)
    vendors = Vendor.objects.filter(startup=startup)
    
    if request.method == 'POST':
        vendor_id = request.POST.get('vendor')
        payable.amount = request.POST.get('amount')
        payable.due_date = request.POST.get('due_date')
        payable.vendor = get_object_or_404(Vendor, pk=vendor_id, startup=startup)
        payable.save()
        messages.success(request, 'Payable updated successfully!')
        return redirect('finance:payable_list')
    
    context = {
        'payable': payable,
        'vendors': vendors,
        'page_title': 'Edit Payable',
        'page_icon': '✏️',
        'page_subtitle': 'Update accounts payable entry',
        'is_edit': True,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'finance/payable_form.html', context)


@login_required
def payable_delete(request, pk):
    """Delete an accounts payable entry."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('finance:finance_dashboard')
    
    payable = get_object_or_404(AccountsPayable, pk=pk, vendor__startup=startup)
    
    if request.method == 'POST':
        vendor_name = payable.vendor.vendor_name
        payable.delete()
        messages.success(request, f'Payable for "{vendor_name}" deleted successfully!')
        return redirect('finance:payable_list')
    
    context = {
        'payable': payable,
        'page_title': 'Delete Payable',
        'page_icon': '🗑️',
        'page_subtitle': 'Confirm deletion of payable entry',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'finance/payable_confirm_delete.html', context)


@login_required
def payable_mark_paid(request, pk):
    """Mark payable as paid."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('finance:finance_dashboard')
    
    payable = get_object_or_404(AccountsPayable, pk=pk, vendor__startup=startup)
    
    if request.method == 'POST':
        payable.paid = True
        payable.save()
        messages.success(request, 'Payable marked as paid!')
        return redirect('finance:payable_list')
    
    context = {
        'payable': payable,
        'page_title': 'Mark as Paid',
        'page_icon': '✅',
        'page_subtitle': 'Confirm payment of payable',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'finance/payable_mark_paid.html', context)


# ============================================
# REIMBURSEMENT VIEWS
# ============================================

@login_required
def reimbursement_list(request):
    """List all reimbursement requests."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        context = {
            'reimbursements': [],
            'total_pending': 0,
            'total_approved': 0,
            'page_title': 'Reimbursements',
            'page_icon': '💳',
            'page_subtitle': 'Manage employee reimbursement requests',
            'is_hr': check_hr_access(request),
            'no_startup': True,
        }
        return render(request, 'finance/reimbursement_list.html', context)
    
    reimbursements = Reimbursement.objects.filter(startup=startup).order_by('-created_at')
    
    total_pending = reimbursements.filter(approved=False).aggregate(Sum('amount'))['amount__sum'] or 0
    total_approved = reimbursements.filter(approved=True).aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'reimbursements': reimbursements,
        'total_pending': total_pending,
        'total_approved': total_approved,
        'page_title': 'Reimbursements',
        'page_icon': '💳',
        'page_subtitle': 'Manage employee reimbursement requests',
        'is_hr': check_hr_access(request),
        'no_startup': False,
    }
    return render(request, 'finance/reimbursement_list.html', context)


@login_required
def reimbursement_create(request):
    """Create a new reimbursement request."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('finance:finance_dashboard')
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        reason = request.POST.get('reason')
        
        if not all([amount, reason]):
            messages.error(request, 'All fields are required.')
            return redirect('finance:reimbursement_create')
        
        Reimbursement.objects.create(
            startup=startup,
            employee=request.user,
            amount=amount,
            reason=reason
        )
        messages.success(request, 'Reimbursement request submitted successfully!')
        return redirect('finance:reimbursement_list')
    
    context = {
        'page_title': 'Request Reimbursement',
        'page_icon': '💳',
        'page_subtitle': 'Submit a new reimbursement request',
        'is_edit': False,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'finance/reimbursement_form.html', context)


@login_required
def reimbursement_edit(request, pk):
    """Edit a reimbursement request."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('finance:finance_dashboard')
    
    reimbursement = get_object_or_404(Reimbursement, pk=pk, startup=startup)
    
    if reimbursement.approved:
        messages.error(request, 'Approved reimbursements cannot be edited.')
        return redirect('finance:reimbursement_list')
    
    if request.method == 'POST':
        reimbursement.amount = request.POST.get('amount')
        reimbursement.reason = request.POST.get('reason')
        reimbursement.save()
        messages.success(request, 'Reimbursement updated successfully!')
        return redirect('finance:reimbursement_list')
    
    context = {
        'reimbursement': reimbursement,
        'page_title': 'Edit Reimbursement',
        'page_icon': '✏️',
        'page_subtitle': 'Update reimbursement request',
        'is_edit': True,
        'is_hr': check_hr_access(request),
    }
    return render(request, 'finance/reimbursement_form.html', context)


@login_required
def reimbursement_delete(request, pk):
    """Delete a reimbursement request."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('finance:finance_dashboard')
    
    reimbursement = get_object_or_404(Reimbursement, pk=pk, startup=startup)
    
    if reimbursement.approved:
        messages.error(request, 'Approved reimbursements cannot be deleted.')
        return redirect('finance:reimbursement_list')
    
    if request.method == 'POST':
        reimbursement.delete()
        messages.success(request, 'Reimbursement deleted successfully!')
        return redirect('finance:reimbursement_list')
    
    context = {
        'reimbursement': reimbursement,
        'page_title': 'Delete Reimbursement',
        'page_icon': '🗑️',
        'page_subtitle': 'Confirm deletion of reimbursement request',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'finance/reimbursement_confirm_delete.html', context)


@login_required
def reimbursement_approve(request, pk):
    """Approve a reimbursement request."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        return redirect('finance:finance_dashboard')
    
    reimbursement = get_object_or_404(Reimbursement, pk=pk, startup=startup)
    
    if reimbursement.approved:
        messages.warning(request, 'This reimbursement is already approved.')
        return redirect('finance:reimbursement_list')
    
    if request.method == 'POST':
        reimbursement.approved = True
        reimbursement.save()
        messages.success(request, 'Reimbursement approved successfully!')
        return redirect('finance:reimbursement_list')
    
    context = {
        'reimbursement': reimbursement,
        'page_title': 'Approve Reimbursement',
        'page_icon': '✅',
        'page_subtitle': 'Review and approve reimbursement request',
        'is_hr': check_hr_access(request),
    }
    return render(request, 'finance/reimbursement_approve.html', context)


# ============================================
# REPORT VIEWS
# ============================================

@login_required
def profit_loss(request):
    """View Profit & Loss statement."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        context = {
            'monthly_data': [],
            'total_income': 0,
            'total_expense': 0,
            'total_profit': 0,
            'year': timezone.now().year,
            'years': range(timezone.now().year - 3, timezone.now().year + 1),
            'page_title': 'Profit & Loss',
            'page_icon': '📈',
            'page_subtitle': 'View your profit and loss statement',
            'is_hr': check_hr_access(request),
            'no_startup': True,
        }
        return render(request, 'finance/profit_loss.html', context)
    
    year = request.GET.get('year', timezone.now().year)
    try:
        year = int(year)
    except:
        year = timezone.now().year
    
    monthly_data = []
    total_income = 0
    total_expense = 0
    
    for month in range(1, 13):
        income = Income.objects.filter(
            startup=startup,
            received_date__month=month,
            received_date__year=year
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        expense = Expense.objects.filter(
            startup=startup,
            expense_date__month=month,
            expense_date__year=year
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        total_income += income
        total_expense += expense
        
        monthly_data.append({
            'month': datetime(year, month, 1).strftime('%B'),
            'income': income,
            'expense': expense,
            'profit': income - expense
        })
    
    total_profit = total_income - total_expense
    
    context = {
        'monthly_data': monthly_data,
        'total_income': total_income,
        'total_expense': total_expense,
        'total_profit': total_profit,
        'year': year,
        'years': range(year - 3, year + 1),
        'page_title': 'Profit & Loss',
        'page_icon': '📈',
        'page_subtitle': 'View your profit and loss statement',
        'is_hr': check_hr_access(request),
        'no_startup': False,
    }
    return render(request, 'finance/profit_loss.html', context)


@login_required
def cash_flow(request):
    """View Cash Flow statement."""
    
    if not check_finance_access(request):
        messages.error(request, 'You do not have permission to access the Finance module.')
        return redirect('people_dashboard')
    
    startup = get_user_startup(request)
    if not startup:
        messages.warning(request, 'No startup associated with your profile.')
        context = {
            'monthly_data': [],
            'total_inflows': 0,
            'total_outflows': 0,
            'total_net': 0,
            'total_income': 0,
            'total_expenses': 0,
            'total_receivables_collected': 0,
            'total_payables_paid': 0,
            'year': timezone.now().year,
            'years': range(timezone.now().year - 3, timezone.now().year + 1),
            'page_title': 'Cash Flow',
            'page_icon': '💳',
            'page_subtitle': 'Track your cash inflows and outflows',
            'is_hr': check_hr_access(request),
            'no_startup': True,
        }
        return render(request, 'finance/cash_flow.html', context)
    
    year = request.GET.get('year', timezone.now().year)
    try:
        year = int(year)
    except:
        year = timezone.now().year
    
    monthly_data = []
    total_inflows = 0
    total_outflows = 0
    total_income = 0
    total_expenses = 0
    total_receivables_collected = 0
    total_payables_paid = 0
    
    for month in range(1, 13):
        # Inflows
        income = Income.objects.filter(
            startup=startup,
            received_date__month=month,
            received_date__year=year
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        receivables = Receivable.objects.filter(
            invoice__startup=startup,
            invoice__created_at__month=month,
            invoice__created_at__year=year,
            paid=True
        ).aggregate(Sum('amount_due'))['amount_due__sum'] or 0
        
        # Outflows
        expenses = Expense.objects.filter(
            startup=startup,
            expense_date__month=month,
            expense_date__year=year
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        payables = AccountsPayable.objects.filter(
            vendor__startup=startup,
            due_date__month=month,
            due_date__year=year,
            paid=True
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        inflows = income + receivables
        outflows = expenses + payables
        net = inflows - outflows
        
        total_inflows += inflows
        total_outflows += outflows
        total_income += income
        total_expenses += expenses
        total_receivables_collected += receivables
        total_payables_paid += payables
        
        monthly_data.append({
            'month': datetime(year, month, 1).strftime('%B'),
            'inflows': inflows,
            'outflows': outflows,
            'net': net
        })
    
    total_net = total_inflows - total_outflows
    
    context = {
        'monthly_data': monthly_data,
        'total_inflows': total_inflows,
        'total_outflows': total_outflows,
        'total_net': total_net,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_receivables_collected': total_receivables_collected,
        'total_payables_paid': total_payables_paid,
        'year': year,
        'years': range(year - 3, year + 1),
        'page_title': 'Cash Flow',
        'page_icon': '💳',
        'page_subtitle': 'Track your cash inflows and outflows',
        'is_hr': check_hr_access(request),
        'no_startup': False,
    }
    return render(request, 'finance/cash_flow.html', context)