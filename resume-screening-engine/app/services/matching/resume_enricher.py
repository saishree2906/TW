from typing import Dict


def enrich_resume_text(resume_data: Dict) -> str:
    """
    Build enriched resume text from structured Phase 2 output.
    """

    skills = ", ".join(resume_data.get("skills", []))
    experience = resume_data.get("experience_years", 0)
    education = ", ".join(resume_data.get("education", []))

    return (
        f"Skills: {skills}. "
        f"Experience: {experience} years. "
        f"Education: {education}."
    )
