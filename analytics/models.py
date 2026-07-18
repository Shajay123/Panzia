from django.db import models
from django.contrib.auth import get_user_model
from startups.models import StartupProfile
from accounts.models import User

User = get_user_model()

class DailySnapshot(models.Model):
    """Daily analytics snapshot for a startup"""
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name='daily_snapshots')
    date = models.DateField(auto_now_add=True)
    
    # Key Metrics
    total_employees = models.IntegerField(default=0)
    active_employees = models.IntegerField(default=0)
    new_employees = models.IntegerField(default=0)
    total_payroll = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Attendance Metrics
    present_count = models.IntegerField(default=0)
    absent_count = models.IntegerField(default=0)
    on_leave_count = models.IntegerField(default=0)
    
    # Performance Metrics
    avg_performance_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    completed_reviews = models.IntegerField(default=0)
    pending_reviews = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['startup', 'date']
        ordering = ['-date']
        verbose_name_plural = "Daily Snapshots"
    
    def __str__(self):
        return f"{self.startup.company_name} - {self.date}"
    
    @property
    def net_profit(self):
        return self.total_revenue - self.total_expenses
    
    @property
    def attendance_rate(self):
        if self.total_employees > 0:
            return (self.present_count / self.total_employees) * 100
        return 0


class WeeklyReport(models.Model):
    """Weekly analytics report"""
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name='weekly_reports')
    week_start = models.DateField()
    week_end = models.DateField()
    week_number = models.IntegerField()
    year = models.IntegerField()
    
    # Summary Metrics
    total_employees = models.IntegerField(default=0)
    new_employees = models.IntegerField(default=0)
    total_payroll = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Attendance Summary
    avg_attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_absent_days = models.IntegerField(default=0)
    total_leave_days = models.IntegerField(default=0)
    
    # Performance Summary
    avg_performance_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    reviews_completed = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['startup', 'week_start', 'year']
        ordering = ['-year', '-week_start']
    
    def __str__(self):
        return f"{self.startup.company_name} - Week {self.week_number} ({self.year})"
    
    @property
    def net_profit(self):
        return self.total_revenue - self.total_expenses


class MonthlyReport(models.Model):
    """Monthly analytics report"""
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name='monthly_reports')
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    
    # Summary Metrics
    total_employees = models.IntegerField(default=0)
    new_employees = models.IntegerField(default=0)
    total_payroll = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Attendance Summary
    avg_attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_absent_days = models.IntegerField(default=0)
    total_leave_days = models.IntegerField(default=0)
    
    # Performance Summary
    avg_performance_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    reviews_completed = models.IntegerField(default=0)
    
    # Growth Metrics
    employee_growth_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    revenue_growth_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['startup', 'month', 'year']
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"{self.startup.company_name} - {self.month} {self.year}"
    
    @property
    def net_profit(self):
        return self.total_revenue - self.total_expenses


class RunwayCalculation(models.Model):
    """Startup runway calculator"""
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name='runway_calculations')
    
    # Inputs
    current_cash = models.DecimalField(max_digits=15, decimal_places=2, help_text="Current cash balance")
    monthly_burn_rate = models.DecimalField(max_digits=15, decimal_places=2, help_text="Monthly burn rate")
    monthly_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Monthly revenue")
    funding_rounds = models.JSONField(default=list, blank=True, help_text="List of funding rounds")
    
    # Results
    runway_months = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    runway_days = models.IntegerField(default=0)
    break_even_month = models.CharField(max_length=20, blank=True, null=True)
    break_even_year = models.IntegerField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Runway Calculations"
    
    def __str__(self):
        return f"{self.startup.company_name} - Runway: {self.runway_months} months"
    
    def calculate_runway(self):
        """Calculate runway based on current cash and burn rate"""
        net_burn = self.monthly_burn_rate - self.monthly_revenue
        if net_burn > 0:
            self.runway_months = self.current_cash / net_burn
            self.runway_days = int(self.runway_months * 30)
        else:
            self.runway_months = 999  # Infinite runway
            self.runway_days = 999
        return self.runway_months


class BurnRateRecord(models.Model):
    """Monthly burn rate tracking"""
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name='burn_rate_records')
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    
    # Financials
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    burn_rate = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cash_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Burn Rate Categories
    payroll_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    operational_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    marketing_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    infrastructure_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    other_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['startup', 'month', 'year']
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"{self.startup.company_name} - {self.month} {self.year}"
    
    @property
    def net_burn(self):
        return self.burn_rate - self.total_revenue


class InvestorReport(models.Model):
    """Investor reports and updates"""
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name='investor_reports')
    
    report_title = models.CharField(max_length=255)
    report_date = models.DateField()
    
    # Key Metrics
    total_employees = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cash_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    runway_months = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Highlights
    key_achievements = models.TextField(blank=True, help_text="Key achievements this period")
    key_challenges = models.TextField(blank=True, help_text="Key challenges faced")
    next_quarter_goals = models.TextField(blank=True, help_text="Goals for next quarter")
    
    # Investor-specific
    funds_raised = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Total funds raised to date")
    valuation = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Current valuation")
    
    is_published = models.BooleanField(default=False)
    pdf_file = models.FileField(upload_to='investor_reports/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-report_date']
    
    def __str__(self):
        return f"{self.startup.company_name} - {self.report_title} ({self.report_date})"
    
    @property
    def net_profit(self):
        return self.total_revenue - self.total_expenses


class LeaderboardEntry(models.Model):
    """Leaderboard for employee performance rankings"""
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name='leaderboard_entries')
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboard_entries')
    
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    
    # Performance metrics
    performance_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    attendance_score = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    project_completion = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    peer_feedback = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rank = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['startup', 'employee', 'month', 'year']
        ordering = ['year', 'month', 'rank']
    
    def __str__(self):
        return f"{self.employee.username} - {self.month} {self.year} (Rank: {self.rank})"
    
    def calculate_total_score(self):
        """Calculate total score based on weighted metrics"""
        weights = {
            'performance_rating': 0.4,
            'attendance_score': 0.2,
            'project_completion': 0.25,
            'peer_feedback': 0.15
        }
        self.total_score = (
            (self.performance_rating * weights['performance_rating']) +
            (self.attendance_score * weights['attendance_score']) +
            (self.project_completion * weights['project_completion']) +
            (self.peer_feedback * weights['peer_feedback'])
        )
        return self.total_score