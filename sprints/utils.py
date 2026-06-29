from .models import Activity


def create_activity(user, action):

    Activity.objects.create(
        user=user,
        action=action
    )


# sprints/utils.py

from .models import Sprint

def update_sprint_progress(sprint):

    total_tasks = sprint.tasks.count()

    completed_tasks = sprint.tasks.filter(
        status='completed'
    ).count()

    if total_tasks == 0:
        return 0

    progress = int(
        (completed_tasks / total_tasks) * 100
    )

    sprint.progress_percentage = progress

    if progress == 100:
        sprint.status = 'completed'

    sprint.save()

    return progress


