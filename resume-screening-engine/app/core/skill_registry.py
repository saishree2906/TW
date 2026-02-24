from typing import Dict, List

# This registry is intentionally simple and configurable.

# app/core/skill_registry.py

SKILL_REGISTRY: Dict[str, List[str]] = {
    "backend_engineer": [
        "python", "java", "sql", "docker", "kubernetes", "aws", "rest", "microservices", "fastapi"
    ],
    "frontend_engineer": [
        "javascript", "typescript", "react", "angular", "vue", "html", "css", "next.js", "tailwind"
    ],
    "full_stack_engineer": [
        "python", "javascript", "react", "node.js", "sql", "aws", "docker", "rest"
    ],
    "data_scientist": [
        "python", "machine learning", "statistics", "pandas", "numpy", "sql", "r", "tensorflow"
    ],
    "devops_engineer": [
        "aws", "azure", "docker", "kubernetes", "jenkins", "terraform", "linux", "ansible"
    ],
}


def get_skills_for_role(role: str | None):
    """
    Return skill list for a given role.

    If role is None or unknown, return empty list.
    This allows pipeline to work without explicit role input.
    """
    if not role:
        return []

    return SKILL_REGISTRY.get(role.lower(), [])
