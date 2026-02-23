from typing import List
from app.core.skill_registry import get_skills_for_role


def extract_jd_skills(job_description: str, role: str) -> List[str]:
    """
    Extract required skills from JD using role-specific skill registry.
    """
    jd_text = job_description.lower()
    role_skills = get_skills_for_role(role)

    extracted = [skill for skill in role_skills if skill in jd_text]

    return sorted(set(extracted))
