# sprints/utils.py

from .models import Sprint, Activity


def create_activity(user, action):
    """Create an activity log entry."""
    Activity.objects.create(
        user=user,
        action=action
    )


# sprints/utils.py

def update_sprint_progress(sprint):
    """
    Update sprint progress based on completed tasks.
    Returns the progress percentage.
    """
    total_tasks = sprint.tasks.count()
    completed_tasks = sprint.tasks.filter(status='completed').count()

    if total_tasks == 0:
        progress = 0
    else:
        progress = int((completed_tasks / total_tasks) * 100)

    # Update the progress field
    sprint.progress = progress
    
    # If all tasks are completed, update sprint status
    if progress == 100 and total_tasks > 0:
        sprint.status = 'completed'
    
    sprint.save()
    
    return progress