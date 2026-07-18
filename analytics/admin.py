from django.contrib import admin
from .models import (
    DailySnapshot, WeeklyReport, MonthlyReport,
    RunwayCalculation, BurnRateRecord, InvestorReport,
    LeaderboardEntry
)

@admin.register(DailySnapshot)
class DailySnapshotAdmin(admin.ModelAdmin):
    list_display = ['startup', 'date', 'total_employees', 'attendance_rate', 'net_profit']
    list_filter = ['startup', 'date']
    search_fields = ['startup__company_name']
    readonly_fields = ['created_at', 'updated_at', 'net_profit', 'attendance_rate']


@admin.register(WeeklyReport)
class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ['startup', 'week_start', 'week_end', 'week_number', 'year']
    list_filter = ['startup', 'year']
    search_fields = ['startup__company_name']
    readonly_fields = ['created_at', 'updated_at', 'net_profit']


@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ['startup', 'month', 'year', 'total_employees', 'net_profit']
    list_filter = ['startup', 'year']
    search_fields = ['startup__company_name']
    readonly_fields = ['created_at', 'updated_at', 'net_profit']


@admin.register(RunwayCalculation)
class RunwayCalculationAdmin(admin.ModelAdmin):
    list_display = ['startup', 'runway_months', 'runway_days', 'created_at']
    list_filter = ['startup']
    search_fields = ['startup__company_name']
    readonly_fields = ['runway_months', 'runway_days', 'created_at', 'updated_at']


@admin.register(BurnRateRecord)
class BurnRateRecordAdmin(admin.ModelAdmin):
    list_display = ['startup', 'month', 'year', 'burn_rate', 'net_burn']
    list_filter = ['startup', 'year']
    search_fields = ['startup__company_name']
    readonly_fields = ['created_at', 'updated_at', 'net_burn']


@admin.register(InvestorReport)
class InvestorReportAdmin(admin.ModelAdmin):
    list_display = ['startup', 'report_title', 'report_date', 'is_published']
    list_filter = ['startup', 'is_published', 'report_date']
    search_fields = ['startup__company_name', 'report_title']
    readonly_fields = ['created_at', 'updated_at', 'net_profit']


@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'year', 'rank', 'total_score']
    list_filter = ['startup', 'month', 'year']
    search_fields = ['employee__username', 'employee__email']
    readonly_fields = ['created_at', 'updated_at']