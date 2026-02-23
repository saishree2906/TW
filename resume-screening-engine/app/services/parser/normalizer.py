
from typing import Dict, Any
import re
from .pii_masker import mask_pii


def _clean_exp(value: Any) -> float:
    """Safety helper to prevent float conversion crashes."""
    try:
        if isinstance(value, str):
            match = re.search(r"(\d+\.?\d*)", value)
            return float(match.group(1)) if match else 0.0
        return float(value or 0.0)
    # except:
    #     return 0.0
    except (ValueError, TypeError, AttributeError):
        return 0.0


def normalize(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Converts raw output to PRD-compliant schema with full PII masking."""
    skills = parsed.get("skills", [])
    raw_exp = parsed.get("experience_years", 0.0)
    education = parsed.get("education", [])
    name = parsed.get("name")
    raw_text = parsed.get("raw_text", "")

    # Correctness: Mask the raw text so Phase 3 (Scoring) is biased-free
    masked_text = mask_pii(raw_text, name)

    return {
        "status": "success",
        "data": {
            "skills": sorted(
                list(set(skills))
            ),  # Efficiency: Remove duplicates
            "experience_years": _clean_exp(raw_exp),
            "education": education,
            "masked_text": masked_text,  # Pass this to the scoring engine
            "contact": {"masked": True, "name_detected": bool(name)},
        },
    }
