
from talents.models import (
    TalentProfile,
    PortfolioProject
)

from certificates.models import Certificate

from reputation.models import (
    ReputationScore
)

from sprints.models import (
    SprintMember
)


# =====================================
# RESUME GENERATOR
# =====================================

def generate_resume(user):

    profile = TalentProfile.objects.filter(
        user=user
    ).first()

    if not profile:
        return "Profile not completed."

    projects = PortfolioProject.objects.filter(
        user=user
    )

    certificates = Certificate.objects.filter(
        user=user
    )

    sprints = SprintMember.objects.filter(
        user=user
    )

    reputation, created = ReputationScore.objects.get_or_create(
        user=user
    )

    resume_text = f"""
{user.username}

{profile.headline}

========================================
PROFESSIONAL SUMMARY
========================================

{profile.bio}

========================================
SKILLS
========================================
"""

    if profile.skills:

        for skill in profile.skills.split(","):

            resume_text += f"• {skill.strip()}\n"

    resume_text += """

========================================
PROJECTS
========================================
"""

    for project in projects:

        resume_text += f"""

PROJECT:
{project.title}

TYPE:
{project.project_type}

DESCRIPTION:
{project.description}

SKILLS:
{project.skills}

"""

    resume_text += """

========================================
CERTIFICATIONS
========================================
"""

    for cert in certificates:

        resume_text += f"• {cert.course.title}\n"

    resume_text += """

========================================
SPRINT EXPERIENCE
========================================
"""

    for sprint in sprints:

        resume_text += f"• {sprint.sprint.title}\n"

    resume_text += f"""

========================================
REPUTATION
========================================

Overall Score : {reputation.overall_score}

Deployment Score : {reputation.deployment_score}

Tier : {reputation.rank_tier}
"""

    return resume_text


# =====================================
# COURSE RECOMMENDATION ENGINE
# =====================================

def recommend_courses(user):

    profile = TalentProfile.objects.filter(
        user=user
    ).first()

    if not profile:
        return []

    user_skills = []

    if profile.skills:

        user_skills = [
            skill.strip().lower()
            for skill in profile.skills.split(",")
        ]

    skill_map = {

        "python": [
            "django",
            "rest api",
            "docker"
        ],

        "django": [
            "rest api",
            "docker",
            "aws"
        ],

        "html": [
            "javascript",
            "react"
        ],

        "react": [
            "nextjs",
            "typescript"
        ],

        "machine learning": [
            "deep learning",
            "llm",
            "langchain"
        ]
    }

    recommendations = []

    for skill in user_skills:

        if skill in skill_map:

            recommendations.extend(
                skill_map[skill]
            )

    return list(set(recommendations))


# =====================================
# JOB MATCH SCORE
# =====================================



def calculate_match_score(job, talent):

    profile = TalentProfile.objects.filter(
        user=talent
    ).first()

    if not profile:
        return 0

    score = 0

    # Skill Matching
    job_skills = [
        x.strip().lower()
        for x in job.skills.split(",")
    ]

    talent_skills = []

    if profile.skills:

        talent_skills = [
            x.strip().lower()
            for x in profile.skills.split(",")
        ]

    matched = len(
        set(job_skills)
        &
        set(talent_skills)
    )

    if job_skills:

        score += (
            matched /
            len(job_skills)
        ) * 40

    # Sprint Experience

    sprint_count = SprintMember.objects.filter(
        user=talent
    ).count()

    score += min(
        sprint_count * 2,
        20
    )

    # Projects

    project_count = PortfolioProject.objects.filter(
        user=talent
    ).count()

    score += min(
        project_count * 3,
        15
    )

    # Certificates

    cert_count = Certificate.objects.filter(
        user=talent
    ).count()

    score += min(
        cert_count * 2,
        15
    )

    # Reputation

    reputation = ReputationScore.objects.filter(
        user=talent
    ).first()

    if reputation:

        score += (
            reputation.overall_score / 100
        ) * 10

    return round(score, 2)

# =====================================
# CAREER ROADMAP
# =====================================

def generate_roadmap(goal):

    if not goal:
        return []

    roadmap = {

        "ai engineer": [

            "Python Advanced",

            "Machine Learning",

            "Deep Learning",

            "OpenAI APIs",

            "LangChain",

            "RAG Systems",

            "AI Deployment"

        ],

        "data scientist": [

            "Python",

            "Statistics",

            "SQL",

            "Pandas",

            "Power BI",

            "Machine Learning"

        ],

        "full stack developer": [

            "HTML",

            "CSS",

            "JavaScript",

            "React",

            "Django",

            "Deployment"

        ]
    }

    return roadmap.get(
        goal.strip().lower(),
        []
    )


# =====================================
# SKILL GAP ANALYSIS
# =====================================

def skill_gap_analysis(
    user,
    target_role
):

    role_skills = {

        "AI Engineer": [

            "Python",

            "Machine Learning",

            "Deep Learning",

            "LangChain",

            "OpenAI APIs"

        ],

        "Data Scientist": [

            "Python",

            "SQL",

            "Statistics",

            "Pandas",

            "Power BI"

        ],

        "Full Stack Developer": [

            "HTML",

            "CSS",

            "JavaScript",

            "React",

            "Django"
        ]
    }

    profile = TalentProfile.objects.filter(
        user=user
    ).first()

    if not profile:
        return []

    current_skills = []

    if profile.skills:

        current_skills = [

            skill.strip().lower()

            for skill in profile.skills.split(",")

        ]

    missing = []

    for skill in role_skills.get(
        target_role,
        []
    ):

        if skill.lower() not in current_skills:

            missing.append(skill)

    return missing

