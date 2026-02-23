from typing import Set, List


def find_missing_skills(
    jd_required_skills: Set[str], resume_skills: Set[str]
) -> List[str]:
    """
    Finds required skills present in JD but missing from resume.
    Deterministic and explainable.
    """
    missing = jd_required_skills - resume_skills
    return sorted(missing)
