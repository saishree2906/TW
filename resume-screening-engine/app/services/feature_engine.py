# app/services/feature_engine.py
import re
from typing import Set
from app.models.resume import ResumeFeatures
import logging

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """
    Enhanced feature extraction with better normalization and skill detection.
    """

    # Skill synonym mapping
    SKILL_SYNONYMS = {
        "python": ["python", "py"],
        "javascript": ["javascript", "js", "nodejs"],
        "java": ["java"],
        "docker": ["docker"],
        "kubernetes": ["kubernetes", "k8s"],
        "aws": ["aws", "amazon web services"],
        "gcp": ["gcp", "google cloud"],
        "azure": ["azure", "microsoft azure"],
        "sql": ["sql", "tsql"],
        "machine learning": ["ml", "machine learning"],
        "deep learning": ["deep learning", "dl"],
        "react": ["react", "reactjs"],
        "angular": ["angular", "angularjs"],
        "fastapi": ["fastapi", "fast api"],
    }

    def __init__(self):
        self.extracted_features_log = []

    def normalize(self, text: str) -> Set[str]:
        """Normalize text and extract tokens with better handling."""
        text = text.lower()
        # Remove special characters but preserve compound terms
        text = re.sub(r"[^a-z0-9+.#\s-]", " ", text)
        tokens = set(text.split())

        # Apply synonym expansion
        expanded = set()
        for token in tokens:
            expanded.add(token)
            # Check if token is synonym for known skill
            for skill, synonyms in self.SKILL_SYNONYMS.items():
                if token in synonyms:
                    expanded.add(skill)

        return expanded

    def extract_resume_features(self, parsed_resume: dict) -> ResumeFeatures:
        """Extract and normalize resume features."""
        raw_text = parsed_resume.get("raw_text", "")

        features = ResumeFeatures(
            candidate_name=parsed_resume.get("name", "Unknown"),
            skills=set(parsed_resume.get("skills", [])),
            experience_years=float(parsed_resume.get("experience_years", 0)),
            education_level=int(parsed_resume.get("education_level", 0)),
            certifications=set(parsed_resume.get("certifications", [])),
            keywords=self.normalize(raw_text),
            languages=set(parsed_resume.get("languages", [])),
            email=parsed_resume.get("email"),
            phone=parsed_resume.get("phone"),
        )

        # Log for analysis
        self.extracted_features_log.append(
            {
                "name": features.candidate_name,
                "skills_count": len(features.skills),
                "keywords_count": len(features.keywords),
            }
        )

        logger.debug(f"Extracted features for {features.candidate_name}")

        return features

    def extract_jd_features(self, jd_text: str) -> dict:
        """Extract job description requirements."""
        tokens = self.normalize(jd_text)

        # Identify likely required skills (skills that appear in JD)
        likely_skills = set()
        for skill, synonyms in self.SKILL_SYNONYMS.items():
            if any(syn in tokens for syn in synonyms):
                likely_skills.add(skill)

        # Extract numeric experience requirement
        exp_match = re.search(
            r"(\d+)\+?\s*(?:years?|yrs?)", jd_text, re.IGNORECASE
        )
        min_exp = float(exp_match.group(1)) if exp_match else 2.0

        return {
            "required_skills": likely_skills,
            "min_experience": min_exp,
            "keywords": tokens,
            "raw_text": jd_text,
        }


# Module-level functions for compatibility
_extractor = FeatureExtractor()


def normalize(text: str) -> Set[str]:
    return _extractor.normalize(text)


def extract_resume_features(parsed_resume: dict) -> ResumeFeatures:
    return _extractor.extract_resume_features(parsed_resume)


def extract_jd_features(jd_text: str) -> dict:
    return _extractor.extract_jd_features(jd_text)
