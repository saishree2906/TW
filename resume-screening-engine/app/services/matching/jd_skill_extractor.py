# from typing import List
# from app.core.skill_registry import get_skills_for_role


# def extract_jd_skills(job_description: str, role: str) -> List[str]:
#     """
#     Extract required skills from JD using role-specific skill registry.
#     """
#     jd_text = job_description.lower()
#     role_skills = get_skills_for_role(role)

#     extracted = [skill for skill in role_skills if skill in jd_text]

#     return sorted(set(extracted))


# app/services/matching/jd_skill_extractor.py

from typing import List
from app.core.skill_registry import get_skills_for_role
from app.services.feature_engine import normalize  # Import Phase 2 normalization

def extract_jd_skills(job_description: str, role: str) -> List[str]:
    """
    Extract required skills from JD using role-specific skill registry.
    Uses normalization to catch synonyms and variations.
    """
    # 1. Normalize the entire JD text
    jd_tokens = normalize(job_description)

    # 2. Get the target skills for the chosen role
    role_skills = get_skills_for_role(role)

    # 3. Match using normalized tokens to catch synonyms (e.g., 'js' matching 'javascript')
    extracted = [
        skill for skill in role_skills
        if skill in jd_tokens
    ]

    return sorted(set(extracted))