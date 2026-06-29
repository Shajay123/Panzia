from talents.models import TalentProfile, PortfolioProject
from certificates.models import Certificate
from sprints.models import SprintMember
from reputation.models import ReputationScore


def build_resume_data(user):

    profile = TalentProfile.objects.filter(
        user=user
    ).first()

    if not profile:
        return {}

    projects = PortfolioProject.objects.filter(
        user=user
    )

    certificates = Certificate.objects.filter(
        user=user
    )

    sprints = SprintMember.objects.filter(
        user=user
    )

    reputation = ReputationScore.objects.filter(
        user=user
    ).first()

    skills = []

    if profile.skills:
        skills = [
            skill.strip()
            for skill in profile.skills.split(",")
        ]

    return {
        "name": user.username,
        "headline": profile.headline,
        "bio": profile.bio,
        "skills": skills,
        "projects": projects,
        "certificates": certificates,
        "sprints": sprints,
        "reputation": reputation
    }