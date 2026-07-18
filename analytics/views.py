from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import datetime, timedelta
import json

from startups.models import StartupProfile
from .models import (
    DailySnapshot, WeeklyReport, MonthlyReport,
    RunwayCalculation, BurnRateRecord, InvestorReport,
    LeaderboardEntry
)
from .forms import (
    DailySnapshotForm, WeeklyReportForm, MonthlyReportForm,
    RunwayCalculationForm, BurnRateRecordForm, InvestorReportForm,
    DateRangeForm
)


@login_required
def analytics_dashboard(request):
    """Main analytics dashboard"""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, "Startup profile not found.")
        return redirect('home')
    
    # Get latest daily snapshot
    latest_snapshot = DailySnapshot.objects.filter(startup=startup).first()
    
    # Get latest monthly report
    latest_monthly = MonthlyReport.objects.filter(startup=startup).first()
    
    # Get latest runway calculation
    latest_runway = RunwayCalculation.objects.filter(startup=startup).first()
    
    # Get latest burn rate
    latest_burn = BurnRateRecord.objects.filter(startup=startup).first()
    
    # Get latest leaderboard entries
    top_performers = LeaderboardEntry.objects.filter(
        startup=startup
    ).order_by('-total_score')[:10]
    
    context = {
        'startup': startup,
        'latest_snapshot': latest_snapshot,
        'latest_monthly': latest_monthly,
        'latest_runway': latest_runway,
        'latest_burn': latest_burn,
        'top_performers': top_performers,
        'page_title': 'Analytics Dashboard',
        'page_icon': '📈',
    }
    return render(request, 'analytics/dashboard.html', context)


@login_required
def daily_snapshot(request):
    """View daily snapshots"""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, "Startup profile not found.")
        return redirect('home')
    
    snapshots = DailySnapshot.objects.filter(startup=startup)
    form = DateRangeForm(request.GET or None)
    
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        if start_date and end_date:
            snapshots = snapshots.filter(date__range=[start_date, end_date])
    
    context = {
        'snapshots': snapshots,
        'form': form,
        'page_title': 'Daily Snapshot',
        'page_icon': '📊',
    }
    return render(request, 'analytics/daily_snapshot.html', context)


@login_required
def daily_snapshot_create(request):
    """Create a new daily snapshot"""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, "Startup profile not found.")
        return redirect('home')
    
    if request.method == 'POST':
        form = DailySnapshotForm(request.POST)
        if form.is_valid():
            snapshot = form.save(commit=False)
            snapshot.startup = startup
            snapshot.save()
            messages.success(request, "Daily snapshot created successfully!")
            return redirect('analytics:daily_snapshot')
    else:
        form = DailySnapshotForm()
    
    context = {
        'form': form,
        'page_title': 'Create Daily Snapshot',
        'page_icon': '📊',
    }
    return render(request, 'analytics/daily_snapshot_form.html', context)


@login_required
def weekly_report(request):
    """View weekly reports"""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, "Startup profile not found.")
        return redirect('home')
    
    reports = WeeklyReport.objects.filter(startup=startup)
    
    context = {
        'reports': reports,
        'page_title': 'Weekly Report',
        'page_icon': '📅',
    }
    return render(request, 'analytics/weekly_report.html', context)


@login_required
def weekly_report_create(request):
    """Create a new weekly report"""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, "Startup profile not found.")
        return redirect('home')
    
    if request.method == 'POST':
        form = WeeklyReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.startup = startup
            report.save()
            messages.success(request, "Weekly report created successfully!")
            return redirect('analytics:weekly_report')
    else:
        form = WeeklyReportForm()
    
    context = {
        'form': form,
        'page_title': 'Create Weekly Report',
        'page_icon': '📅',
    }
    return render(request, 'analytics/weekly_report_form.html', context)


@login_required
def monthly_report(request):
    """View monthly reports"""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, "Startup profile not found.")
        return redirect('home')
    
    reports = MonthlyReport.objects.filter(startup=startup)
    
    context = {
        'reports': reports,
        'page_title': 'Monthly Report',
        'page_icon': '📆',
    }
    return render(request, 'analytics/monthly_report.html', context)


@login_required
def monthly_report_create(request):
    """Create a new monthly report"""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, "Startup profile not found.")
        return redirect('home')
    
    if request.method == 'POST':
        form = MonthlyReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.startup = startup
            report.save()
            messages.success(request, "Monthly report created successfully!")
            return redirect('analytics:monthly_report')
    else:
        form = MonthlyReportForm()
    
    context = {
        'form': form,
        'page_title': 'Create Monthly Report',
        'page_icon': '📆',
    }
    return render(request, 'analytics/monthly_report_form.html', context)


@login_required
def runway_calculator(request):
    """Runway calculator view"""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, "Startup profile not found.")
        return redirect('home')
    
    calculations = RunwayCalculation.objects.filter(startup=startup)
    
    context = {
        'calculations': calculations,
        'page_title': 'Runway Calculator',
        'page_icon': '✈️',
    }
    return render(request, 'analytics/runway_calculator.html', context)


@login_required
def runway_calculate(request):
    """Calculate runway"""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, "Startup profile not found.")
        return redirect('home')
    
    if request.method == 'POST':
        form = RunwayCalculationForm(request.POST)
        if form.is_valid():
            calc = form.save(commit=False)
            calc.startup = startup
            calc.calculate_runway()
            calc.save()
            messages.success(request, f"Runway calculated: {calc.runway_months} months")
            return redirect('analytics:runway_calculator')
    else:
        form = RunwayCalculationForm()
    
    context = {
        'form': form,
        'page_title': 'Calculate Runway',
        'page_icon': '✈️',
    }
    return render(request, 'analytics/runway_calculator_form.html', context)


@login_required
def burn_rate(request):
    """View burn rate records"""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, "Startup profile not found.")
        return redirect('home')
    
    records = BurnRateRecord.objects.filter(startup=startup)
    
    context = {
        'records': records,
        'page_title': 'Burn Rate',
        'page_icon': '🔥',
    }
    return render(request, 'analytics/burn_rate.html', context)


@login_required
def burn_rate_create(request):
    """Create a new burn rate record"""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, "Startup profile not found.")
        return redirect('home')
    
    if request.method == 'POST':
        form = BurnRateRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.startup = startup
            record.save()
            messages.success(request, "Burn rate record created successfully!")
            return redirect('analytics:burn_rate')
    else:
        form = BurnRateRecordForm()
    
    context = {
        'form': form,
        'page_title': 'Create Burn Rate Record',
        'page_icon': '🔥',
    }
    return render(request, 'analytics/burn_rate_form.html', context)


@login_required
def investor_reports(request):
    """View investor reports"""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, "Startup profile not found.")
        return redirect('home')
    
    reports = InvestorReport.objects.filter(startup=startup)
    
    context = {
        'reports': reports,
        'page_title': 'Investor Reports',
        'page_icon': '📄',
    }
    return render(request, 'analytics/investor_reports.html', context)


@login_required
def investor_report_create(request):
    """Create a new investor report"""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, "Startup profile not found.")
        return redirect('home')
    
    if request.method == 'POST':
        form = InvestorReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.startup = startup
            report.save()
            messages.success(request, "Investor report created successfully!")
            return redirect('analytics:investor_reports')
    else:
        form = InvestorReportForm()
    
    context = {
        'form': form,
        'page_title': 'Create Investor Report',
        'page_icon': '📄',
    }
    return render(request, 'analytics/investor_report_form.html', context)


@login_required
def investor_report_detail(request, pk):
    """View investor report details"""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, "Startup profile not found.")
        return redirect('home')
    
    report = get_object_or_404(InvestorReport, pk=pk, startup=startup)
    
    context = {
        'report': report,
        'page_title': report.report_title,
        'page_icon': '📄',
    }
    return render(request, 'analytics/investor_report_detail.html', context)


@login_required
def leaderboard(request):
    """View leaderboard"""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, "Startup profile not found.")
        return redirect('home')
    
    # Get current month and year
    current_month = timezone.now().strftime('%B')
    current_year = timezone.now().year
    
    entries = LeaderboardEntry.objects.filter(
        startup=startup
    ).select_related('employee')
    
    # Filter by month if provided
    month = request.GET.get('month', current_month)
    year = request.GET.get('year', current_year)
    
    if month:
        entries = entries.filter(month=month)
    if year:
        entries = entries.filter(year=year)
    
    entries = entries.order_by('rank')[:20]
    
    context = {
        'entries': entries,
        'current_month': current_month,
        'current_year': current_year,
        'selected_month': month,
        'selected_year': year,
        'page_title': 'Leaderboard',
        'page_icon': '🏆',
    }
    return render(request, 'analytics/leaderboard.html', context)


@login_required
def monthly_rankings(request):
    """View monthly rankings"""
    try:
        startup = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        messages.error(request, "Startup profile not found.")
        return redirect('home')
    
    # Get all months with rankings
    months = LeaderboardEntry.objects.filter(
        startup=startup
    ).values('month', 'year').distinct().order_by('-year', '-month')
    
    context = {
        'months': months,
        'page_title': 'Monthly Rankings',
        'page_icon': '📊',
    }
    return render(request, 'analytics/monthly_rankings.html', context)