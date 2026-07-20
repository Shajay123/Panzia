from django.db import models
from django.conf import settings
from startups.models import StartupProfile


# ======================================
# SPRINT CATEGORY
# ======================================

class SprintCategory(models.TextChoices):
    UI_UX = "UI/UX", "UI/UX"
    FRONTEND = "Frontend", "Frontend"
    BACKEND = "Backend", "Backend"
    MARKETING = "Marketing", "Marketing"
    CONTENT = "Content", "Content"
    RESEARCH = "Research", "Research"
    AI = "AI", "AI"
    AUTOMATION = "Automation", "Automation"
    OPERATIONS = "Operations", "Operations"
    COMMUNITY = "Community", "Community"
    OTHER = "Other", "Other"


# ======================================
# SKILLS
# ======================================

class Skill(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    def __str__(self):
        return self.name


# ======================================
# SPRINT
# ======================================

class Sprint(models.Model):

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    )

    startup = models.ForeignKey(
    StartupProfile,
    on_delete=models.CASCADE,
    related_name='sprints'
    )

    title = models.CharField(max_length=255)

    description = models.TextField()

    domain = models.CharField(max_length=100)

    category = models.CharField(
        max_length=20,
        choices=SprintCategory.choices,
        default=SprintCategory.OTHER
    )

    required_skills = models.ManyToManyField(
        Skill,
        blank=True
    )

    deadline = models.DateField()

    max_contributors = models.PositiveIntegerField(default=5)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def progress_percentage(self):
        total_tasks = self.tasks.count()

        if not total_tasks:
            return 0

        completed_tasks = self.tasks.filter(
            status='completed'
        ).count()

        return round(
            (completed_tasks / total_tasks) * 100
        )
    
    def __str__(self):
        return self.title


# ======================================
# SPRINT APPLICATION
# ======================================

class SprintApplication(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    sprint = models.ForeignKey(
        Sprint,
        on_delete=models.CASCADE,
        related_name='applications'
    )

    talent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.talent.username} - {self.sprint.title}"


# ======================================
# SPRINT MEMBER
# ======================================

class SprintMember(models.Model):

    sprint = models.ForeignKey(
        Sprint,
        on_delete=models.CASCADE,
        related_name='members'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.sprint.title}"


# ======================================
# TASK
# ======================================

class Task(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('progress', 'In Progress'),
        ('review', 'Review'),
        ('completed', 'Completed'),
    )

    sprint = models.ForeignKey(
        Sprint,
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    title = models.CharField(max_length=255)

    description = models.TextField()

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    deadline = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ======================================
# SUBMISSION
# ======================================

class Submission(models.Model):

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='submissions'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    github_url = models.URLField(
        blank=True,
        null=True
    )

    drive_url = models.URLField(
        blank=True,
        null=True
    )

    notes = models.TextField(blank=True, default='')
    
    reviewed = models.BooleanField(
        default=False
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    submitted_at = models.DateTimeField(auto_now_add=True)
    
    # ✅ NEW: Rejection reason
    rejection_reason = models.TextField(
        blank=True,
        default=''
    )

    def __str__(self):
        return f"{self.user.username} - {self.task.title}"

# ======================================
# SPRINT ROLE
# ======================================

class SprintRole(models.Model):

    sprint = models.ForeignKey(
        Sprint,
        on_delete=models.CASCADE,
        related_name='roles'
    )

    role_name = models.CharField(max_length=100)

    openings = models.PositiveIntegerField(default=1)

    description = models.TextField()

    def __str__(self):
        return f"{self.role_name} ({self.sprint.title})"


# ======================================
# ACTIVITY LOG
# ======================================

class Activity(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    action = models.CharField(max_length=255)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.action




class SprintProject(models.Model):

    sprint = models.ForeignKey(
        Sprint,
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    submission_file = models.FileField(
        upload_to="sprint_projects/"
    )

    startup_rating = models.IntegerField(
        default=0
    )

    added_to_portfolio = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )