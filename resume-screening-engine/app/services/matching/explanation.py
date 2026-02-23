"""
Enhanced explanation generation with dynamic, multi-factor analysis.

Generates comprehensive explanations instead of static templates,
considering skills, experience, education, and certifications.
"""

from typing import List, Dict, Set
from datetime import datetime


class ExplanationGenerator:
    """
    Generate dynamic, data-driven explanations.
    Factors in multiple dimensions: skills, experience, education, certifications.
    """

    SKILL_CATEGORIES = {
        "programming": ["python", "java", "c++", "javascript", "rust"],
        "frontend": ["react", "angular", "vue", "html", "css"],
        "backend": ["fastapi", "django", "flask", "spring", "nodejs"],
        "data": ["pandas", "numpy", "tensorflow", "pytorch", "spark"],
        "devops": ["docker", "kubernetes", "aws", "terraform", "jenkins"],
        "databases": ["sql", "mongodb", "postgres", "dynamodb", "redis"],
    }

    def __init__(self):
        self.generated_explanations = []

    def generate(
        self,
        resume_skills: Set[str],
        required_skills: Set[str],
        experience_years: float,
        min_experience: float,
        match_score: float,
        certifications: Set[str] = None,
        education_level: int = 0,
    ) -> Dict:
        """
        Generate comprehensive explanation with multiple factors.

        Returns:
            {
                "summary": str,
                "strengths": List[str],
                "weaknesses": List[str],
                "gaps": List[str],
                "readiness": str,
                "detailed_analysis": str
            }
        """
        if certifications is None:
            certifications = set()

        matched_skills = resume_skills & required_skills
        missing_skills = required_skills - resume_skills
        extra_skills = resume_skills - required_skills
        experience_gap = max(min_experience - experience_years, 0)

        strengths = self._identify_strengths(
            matched_skills,
            extra_skills,
            experience_years,
            min_experience,
            certifications,
        )
        weaknesses = self._identify_weaknesses(
            missing_skills, experience_gap, education_level
        )
        gaps = self._analyze_gaps(missing_skills, experience_gap, match_score)

        readiness = self._assess_readiness(
            match_score,
            experience_gap,
            len(matched_skills),
            len(required_skills),
        )

        summary = self._generate_summary(
            match_score,
            len(matched_skills),
            len(required_skills),
            experience_gap,
            readiness,
        )

        detailed = self._generate_detailed_analysis(
            matched_skills,
            missing_skills,
            experience_gap,
            certifications,
            match_score,
        )

        result = {
            "summary": summary,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "gaps": gaps,
            "readiness": readiness,
            "detailed_analysis": detailed,
            "metrics": {
                "skill_match_count": len(matched_skills),
                "total_required_skills": len(required_skills),
                "skill_match_percentage": round(
                    (len(matched_skills) / max(len(required_skills), 1)) * 100,
                    2,
                ),
                "experience_gap_years": round(experience_gap, 1),
                "overall_score": round(match_score, 2),
            },
        }

        # Store for learning purposes
        self.generated_explanations.append(
            {"timestamp": datetime.now().isoformat(), "result": result}
        )

        return result

    def _identify_strengths(
        self,
        matched: Set[str],
        extra: Set[str],
        exp_years: float,
        min_exp: float,
        certs: Set[str],
    ) -> List[str]:
        """Identify candidate strengths."""
        strengths = []

        # Core skill strengths
        if matched:
            primary = [
                s
                for s in matched
                if s in self.SKILL_CATEGORIES.get("programming", [])
            ]
            if primary:
                strengths.append(
                    f"Strong programming foundation with {', '.join(primary)}"
                )
            secondary = matched - set(primary)
            if secondary:
                strengths.append(
                    f"Additional expertise in {', '.join(sorted(secondary))}"
                )

        # Experience strength
        if exp_years >= min_exp:
            strengths.append(
                f"Meets experience requirement with {exp_years} years"
            )
        elif exp_years > 0:
            strengths.append(f"Has practical experience ({exp_years} years)")

        # Extra skills (bonus)
        if extra:
            top_extra = sorted(list(extra))[:3]
            strengths.append(
                f"Brings additional skills: {', '.join(top_extra)}"
            )

        # Certifications
        if certs:
            strengths.append(
                f"Holds relevant certifications: {', '.join(sorted(certs)[:3])}"
            )

        return strengths[:5]  # Limit to top 5

    def _identify_weaknesses(
        self, missing: Set[str], exp_gap: float, edu_level: int
    ) -> List[str]:
        """Identify candidate weaknesses."""
        weaknesses = []

        if missing:
            critical = sorted(list(missing))[:3]
            weaknesses.append(
                f"Missing critical skills: {', '.join(critical)}"
            )

        if exp_gap > 0:
            weaknesses.append(
                f"Experience gap of {exp_gap:.1f} years below requirement"
            )

        if edu_level < 2:
            weaknesses.append("Education level below typical requirement")

        return weaknesses

    def _analyze_gaps(
        self, missing: Set[str], exp_gap: float, score: float
    ) -> List[str]:
        """Analyze skill and experience gaps."""
        gaps = []

        if missing:
            by_category = self._categorize_missing(missing)
            for category, skills in by_category.items():
                gaps.append(
                    f"{category.title()}: missing {', '.join(sorted(skills)[:3])}"
                )

        if exp_gap > 0:
            gaps.append(f"Experience: {exp_gap:.1f} years behind requirement")

        return gaps

    def _assess_readiness(
        self,
        score: float,
        exp_gap: float,
        matched_count: int,
        required_count: int,
    ) -> str:
        """Assess overall readiness level."""
        if score >= 80:
            return "Ready for immediate consideration"
        elif score >= 60 and exp_gap <= 1:
            return "Promising candidate with some development needed"
        elif score >= 50:
            return "Potential with targeted training"
        else:
            return "Requires significant development"

    def _generate_summary(
        self,
        score: float,
        matched: int,
        required: int,
        exp_gap: float,
        readiness: str,
    ) -> str:
        """Generate concise summary."""
        match_pct = round((matched / max(required, 1)) * 100, 1)

        return (
            f"Candidate scores {score:.1f}% with {match_pct}% skill match "
            f"({matched}/{required} required skills). "
            f"Experience gap: {exp_gap:.1f} years. "
            f"Readiness: {readiness}."
        )

    def _generate_detailed_analysis(
        self,
        matched: Set[str],
        missing: Set[str],
        exp_gap: float,
        certs: Set[str],
        score: float,
    ) -> str:
        """Generate detailed, narrative analysis."""
        analysis = []

        analysis.append(
            f"This candidate demonstrates a {score:.1f}% alignment with "
            f"the position requirements."
        )

        if matched:
            top_matched = sorted(list(matched)[:5])
            analysis.append(
                f"Core competencies include {', '.join(top_matched)}."
            )

        if missing:
            top_missing = sorted(list(missing)[:5])
            analysis.append(
                f"Key areas for development: {', '.join(top_missing)}."
            )

        if certs:
            analysis.append(
                f"Relevant certifications: {', '.join(sorted(certs))}."
            )

        if exp_gap > 0:
            analysis.append(
                f"Additional {exp_gap:.1f} years of experience would "
                f"strengthen candidacy."
            )
        else:
            analysis.append("Meets or exceeds experience expectations.")

        return " ".join(analysis)

    def _categorize_missing(self, missing: Set[str]) -> Dict[str, Set[str]]:
        """Categorize missing skills by type."""
        categorized = {}
        for category, skills in self.SKILL_CATEGORIES.items():
            missing_in_cat = missing & set(skills)
            if missing_in_cat:
                categorized[category] = missing_in_cat
        return categorized


def generate_explanation(resume, jd, score):
    """Legacy interface for backward compatibility."""
    generator = ExplanationGenerator()
    result = generator.generate(
        resume_skills=getattr(resume, "skills", set()),
        required_skills=jd.get("required_skills", set()),
        experience_years=getattr(resume, "experience_years", 0),
        min_experience=jd.get("min_experience", 2.0),
        match_score=score,
        certifications=getattr(resume, "certifications", set()),
        education_level=getattr(resume, "education_level", 0),
    )

    return {
        "strengths": result["strengths"],
        "missing_skills": list(
            jd.get("required_skills", set()) - getattr(resume, "skills", set())
        ),
        "experience_gap": max(
            jd.get("min_experience", 2.0)
            - getattr(resume, "experience_years", 0),
            0,
        ),
        "explanation": result["summary"],
        "detailed_analysis": result["detailed_analysis"],
        "readiness": result["readiness"],
    }
