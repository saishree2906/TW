from typing import Dict, List

# This registry is intentionally simple and configurable.

SKILL_REGISTRY: Dict[str, List[str]] = {
    "backend_engineer": [
        "python",
        "java",
        "sql",
        "docker",
        "kubernetes",
        "aws",
        "rest",
        "microservices",
    ],
    "data_scientist": [
        "python",
        "machine learning",
        "statistics",
        "pandas",
        "numpy",
        "sql",
        "r",
    ],
    "devops_engineer": [
        "aws",
        "azure",
        "docker",
        "kubernetes",
        "jenkins",
        "terraform",
        "linux",
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
