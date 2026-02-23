# app/services/scoring.py
from typing import Dict, Set
from math import log1p

# import json


class AdvancedScoringEngine:
    """
    Sophisticated resume scoring with multiple weighted factors.
    Includes fuzzy matching, skill categories, and nuanced metrics.
    """

    # Skill importance weights by category
    SKILL_IMPORTANCE = {
        "critical": 1.0,  # Must-have skills
        "important": 0.7,  # Highly desirable
        "nice_to_have": 0.4,  # Bonus
    }

    # Experience scoring formula
    EXP_MIN_THRESHOLD = 0.5
    EXP_MAX_THRESHOLD = 10.0

    def __init__(self):
        self.scoring_history = []

    def calculate_match_score(
        self, resume, jd: Dict, verbose: bool = False
    ) -> Dict:
        """
        Calculate comprehensive match score.

        Returns:
            {
                "overall_score": float (0-100),
                "skill_score": float (0-100),
                "experience_score": float (0-100),
                "education_score": float (0-100),
                "keyword_score": float (0-100),
                "component_scores": Dict,
                "confidence": float (0-1)
            }
        """
        resume_skills = getattr(resume, "skills", set())
        resume_exp = getattr(resume, "experience_years", 0)
        resume_edu = getattr(resume, "education_level", 0)
        resume_keywords = getattr(resume, "keywords", set())
        resume_certs = getattr(resume, "certifications", set())

        required_skills = jd.get("required_skills", set())
        min_exp = jd.get("min_experience", 2.0)
        jd_keywords = jd.get("keywords", set())

        # Calculate component scores
        skill_score = self._score_skills(
            resume_skills, required_skills, resume_certs
        )
        exp_score = self._score_experience(resume_exp, min_exp)
        edu_score = self._score_education(
            resume_edu, jd.get("min_education", 2)
        )
        keyword_score = self._score_keywords(resume_keywords, jd_keywords)

        # Weighted aggregate
        overall = (
            0.40 * skill_score
            + 0.25 * exp_score
            + 0.15 * edu_score
            + 0.20 * keyword_score
        )

        # Confidence based on completeness
        confidence = self._calculate_confidence(resume, jd)

        result = {
            "overall_score": round(overall, 2),
            "skill_score": round(skill_score, 2),
            "experience_score": round(exp_score, 2),
            "education_score": round(edu_score, 2),
            "keyword_score": round(keyword_score, 2),
            "component_scores": {
                "skills": round(skill_score, 2),
                "experience": round(exp_score, 2),
                "education": round(edu_score, 2),
                "keywords": round(keyword_score, 2),
            },
            "confidence": round(confidence, 2),
        }

        # Store for learning
        self.scoring_history.append(
            {
                "resume": getattr(resume, "candidate_name", "Unknown"),
                "scores": result,
            }
        )

        if verbose:
            result["breakdown"] = {
                "matched_skills": list(resume_skills & required_skills),
                "missing_skills": list(required_skills - resume_skills),
                "extra_skills": list(resume_skills - required_skills),
                "experience_gap": max(min_exp - resume_exp, 0),
            }

        return result

    def _score_skills(
        self,
        resume_skills: Set[str],
        required: Set[str],
        certifications: Set[str],
    ) -> float:
        """
        Score skills with bonus for certifications.
        Range: 0-100
        """
        if not required:
            return 100.0 if resume_skills else 50.0

        matched = resume_skills & required
        match_rate = len(matched) / len(required)
        base_score = match_rate * 100

        # Certification bonus
        cert_bonus = min(len(certifications) * 5, 10)

        return min(base_score + cert_bonus, 100.0)

    def _score_experience(self, resume_exp: float, min_exp: float) -> float:
        """
        Score experience using logarithmic curve.
        Penalizes below minimum, rewards above.
        """
        if resume_exp < self.EXP_MIN_THRESHOLD:
            return (resume_exp / max(min_exp, 0.5)) * 50

        if resume_exp >= min_exp:
            excess = resume_exp - min_exp
            bonus = min(log1p(excess) * 10, 30)
            return min(70 + bonus, 100.0)

        gap = min_exp - resume_exp
        penalty = (gap / min_exp) * 40
        return max(60 - penalty, 0)

    def _score_education(self, resume_edu: int, required_edu: int) -> float:
        """
        Score education level.
        0: No degree, 1: Diploma, 2: Bachelor, 3: Master, 4: PhD
        """
        if resume_edu >= required_edu:
            return 100.0
        if resume_edu >= required_edu - 1:
            return 80.0
        if resume_edu > 0:
            return 50.0 + (resume_edu / max(required_edu, 1)) * 30
        return 30.0

    def _score_keywords(
        self, resume_keywords: Set[str], jd_keywords: Set[str]
    ) -> float:
        """
        Score keyword match (broader than skill matching).
        """
        if not jd_keywords:
            return 100.0

        matched = resume_keywords & jd_keywords
        match_rate = len(matched) / len(jd_keywords)
        return min(match_rate * 100, 100.0)

    def _calculate_confidence(self, resume, jd: Dict) -> float:
        """
        Calculate confidence score (0-1) based on data completeness.
        """
        confidence = 0.5

        # Skills data
        if getattr(resume, "skills", set()):
            confidence += 0.15

        # Experience data
        if getattr(resume, "experience_years", 0) > 0:
            confidence += 0.15

        # Education data
        if getattr(resume, "education_level", 0) > 0:
            confidence += 0.1

        # Certifications
        if getattr(resume, "certifications", set()):
            confidence += 0.1

        return min(confidence, 1.0)


def calculate_match_score(resume, jd):
    """Legacy interface for backward compatibility."""
    engine = AdvancedScoringEngine()
    result = engine.calculate_match_score(resume, jd, verbose=False)
    return result["overall_score"]
