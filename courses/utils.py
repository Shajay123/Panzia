from sprints.models import Sprint


def get_recommended_sprints(course):

    skills = []

    for module in course.modules.all():

        if module.skill_tags:

            skills.extend([
                skill.strip().lower()
                for skill in module.skill_tags.split(",")
            ])

    skills = list(set(skills))

    recommendations = []

    sprints = Sprint.objects.filter(
        status="open"
    )

    for sprint in sprints:

        sprint_skills = [
            skill.strip().lower()
            for skill in sprint.required_skills.split(",")
        ]

        score = len(
            set(skills) &
            set(sprint_skills)
        )

        if score > 0:

            recommendations.append(
                (score, sprint)
            )

    recommendations.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    return [
        sprint
        for score, sprint in recommendations
    ][:5]