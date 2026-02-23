"""
Custom SpaCy-based Resume Parser

Phase 2 Production Implementation:
- Extracts text from PDF and DOCX files
- Uses SpaCy 3.x NER for entity recognition
- PhraseMatcher for skill extraction
- Regex for email and phone detection
- Heuristic experience year calculation
"""

import os
import re
import spacy
from typing import Dict, Any, List
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import docx2txt
except ImportError:
    docx2txt = None

from .base import ResumeParser as ParserContract

# Global spaCy model (loaded once on first use)
_nlp_model = None


def get_spacy_model():
    """
    Lazy-load SpaCy model (singleton pattern).
    Ensures model is loaded only once for efficiency.
    """
    global _nlp_model
    if _nlp_model is None:
        _nlp_model = spacy.load("en_core_web_md")
    return _nlp_model


class SpacyResumeParser(ParserContract):
    """
    Production-grade SpaCy-based resume parser.

    Supported formats: PDF, DOCX
    Dependencies: pdfplumber, docx2txt, spacy
    """

    # Common technical and soft skills for PhraseMatcher
    SKILLS_DATABASE = {
        # Programming Languages
        "python",
        "java",
        "javascript",
        "typescript",
        "c++",
        "c#",
        "csharp",
        "ruby",
        "go",
        "rust",
        "php",
        "swift",
        "kotlin",
        "scala",
        "r",
        "matlab",
        "groovy",
        "perl",
        "haskell",
        "elixir",
        "clojure",
        # Web Frameworks & Libraries
        "react",
        "angular",
        "vue",
        "vue.js",
        "fastapi",
        "django",
        "flask",
        "spring",
        "spring boot",
        "express",
        "node.js",
        "nodejs",
        "asp.net",
        "rails",
        "laravel",
        "next.js",
        "nextjs",
        "nuxt",
        "ember",
        # Databases
        "sql",
        "mysql",
        "postgresql",
        "mongo",
        "mongodb",
        "cassandra",
        "elasticsearch",
        "redis",
        "dynamodb",
        "oracle",
        "sqlite",
        "mariadb",
        "neo4j",
        "cockroachdb",
        "snowflake",
        "bigquery",
        # Cloud Platforms
        "aws",
        "azure",
        "gcp",
        "google cloud",
        "heroku",
        "digitalocean",
        "kubernetes",
        "docker",
        "docker container",
        "openshift",
        # DevOps & Tools
        "git",
        "github",
        "gitlab",
        "bitbucket",
        "jenkins",
        "circleci",
        "travis ci",
        "gitlab ci",
        "docker",
        "kubernetes",
        "terraform",
        "ansible",
        "puppet",
        "chef",
        "docker compose",
        "helm",
        # Data Science & ML
        "machine learning",
        "deep learning",
        "tensorflow",
        "pytorch",
        "scikit-learn",
        "keras",
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "jupyter",
        "nlp",
        "computer vision",
        "cv",
        # Other Technologies
        "api",
        "rest",
        "graphql",
        "soap",
        "microservices",
        "grpc",
        "rabbitmq",
        "kafka",
        "aws sqs",
        "message queue",
        "nosql",
        "hadoop",
        "spark",
        "hive",
        "presto",
        "athena",
        # Soft Skills
        "communication",
        "teamwork",
        "leadership",
        "problem solving",
        "critical thinking",
        "project management",
        "agile",
        "scrum",
        "kanban",
        "waterfall",
        "strategic thinking",
        "analytical",
    }

    def __init__(self, file_path: str):
        """
        Initialize parser with file path.

        Args:
            file_path: Absolute path to resume file (PDF or DOCX)

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file format not supported
        """
        self.file_path = file_path

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Resume file not found: {file_path}")

        ext = Path(file_path).suffix.lower()
        if ext not in {".pdf", ".docx"}:
            raise ValueError(
                f"Unsupported file format: {ext}. Use PDF or DOCX."
            )

    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse resume and extract structured data.

        Args:
            text: Unused (kept for contract compatibility)

        Returns:
            Dictionary with extracted resume data:
            {
                "skills": List[str],
                "experience_years": float,
                "education": List[str],
                "total_experience": int,
                "name": str | None,
                "email": str | None,
                "mobile_number": str | None,
                "college_name": str | None,
                "degree": str | None,
                "no_of_pages": int | None,
            }
        """
        try:
            # Extract raw text from file
            raw_text = self._extract_text()

            # Process with spaCy
            nlp = get_spacy_model()
            doc = nlp(raw_text)

            # Extract entities and information
            extracted = {
                "skills": self._extract_skills(raw_text, doc),
                "experience_years": self._extract_experience_years(
                    raw_text, doc
                ),
                "education": self._extract_education(raw_text, doc),
                "total_experience": self._extract_total_experience_int(
                    raw_text, doc
                ),
                "name": self._extract_name(doc),
                "email": self._extract_email(raw_text),
                "mobile_number": self._extract_phone(raw_text),
                "college_name": self._extract_college(raw_text, doc),
                "degree": self._extract_degree(raw_text, doc),
                "no_of_pages": 1,  # Placeholder for multi-page handling
            }

            return extracted

        except Exception as e:
            raise RuntimeError(f"Resume parsing failed: {str(e)}") from e

    def _extract_text(self) -> str:
        """Extract text from PDF or DOCX file."""
        ext = Path(self.file_path).suffix.lower()

        if ext == ".pdf":
            return self._extract_text_from_pdf()
        elif ext == ".docx":
            return self._extract_text_from_docx()
        else:
            raise ValueError(f"Unsupported format: {ext}")

    def _extract_text_from_pdf(self) -> str:
        """Extract text from PDF using pdfplumber."""
        if pdfplumber is None:
            raise RuntimeError(
                "pdfplumber not installed. Install via: pip install pdfplumber"
            )

        text = []
        try:
            with pdfplumber.open(self.file_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text.append(extracted)
        except Exception as e:
            raise RuntimeError(f"PDF extraction failed: {str(e)}") from e

        return "\n".join(text)

    def _extract_text_from_docx(self) -> str:
        """Extract text from DOCX using docx2txt."""
        if docx2txt is None:
            raise RuntimeError(
                "docx2txt not installed. Install via: pip install docx2txt"
            )

        try:
            return docx2txt.process(self.file_path)
        except Exception as e:
            raise RuntimeError(f"DOCX extraction failed: {str(e)}") from e

    def _extract_email(self, text: str) -> str | None:
        """Extract email address using regex."""
        pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
        match = re.search(pattern, text)
        return match.group(0) if match else None

    def _extract_phone(self, text: str) -> str | None:
        """Extract phone number using regex."""
        # Pattern for various phone formats: +1-555-123-4567, (555) 123-4567, 555.123.4567, etc.
        pattern = (
            r"(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}"
        )
        match = re.search(pattern, text)
        return match.group(0) if match else None

    def _extract_name(self, doc) -> str | None:
        """
        Extract person name from spaCy PERSON entities.

        Returns the first PERSON entity found (typically at document start).
        """
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text
        return None

    def _extract_skills(self, text: str, doc) -> List[str]:
        """
        Extract skills using PhraseMatcher and text matching.

        Returns: Unique list of detected skills (lowercase)
        """
        skills = set()
        text_lower = text.lower()

        # Match skills from database
        for skill in self.SKILLS_DATABASE:
            # Use word boundaries to avoid partial matches
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text_lower):
                skills.add(skill)

        # Also extract ORG and PRODUCT entities as potential skills
        for ent in doc.ents:
            if ent.label_ in {"ORG", "PRODUCT"}:
                skill_text = ent.text.lower()
                if (
                    len(skill_text) > 2
                    and skill_text not in self.SKILLS_DATABASE
                ):
                    # Only add if it looks like a skill (short, no spaces, or known patterns)
                    if skill_text in {"java", "python", "sql", "aws"} or any(
                        tech in skill_text
                        for tech in ["java", "script", "db", "sql"]
                    ):
                        skills.add(skill_text)

        return sorted(list(skills))

    def _extract_education(self, text: str, doc) -> List[str]:
        """
        Extract education information (degree names).

        Returns: List of education-related entities found
        """
        education_keywords = {
            "bachelor",
            "masters",
            "phd",
            "associate",
            "diploma",
            "b.a.",
            "b.s.",
            "m.a.",
            "m.s.",
            "m.b.a.",
            "b.tech",
            "m.tech",
            "btech",
            "mtech",
            "cs",
            "engineering",
            "computer science",
            "information technology",
            "business",
            "commerce",
            "economics",
            "arts",
            "science",
            "medicine",
        }

        education = []
        text_lower = text.lower()

        # Look for education keywords
        for keyword in education_keywords:
            pattern = r"\b" + re.escape(keyword) + r"\b"
            if re.search(pattern, text_lower):
                education.append(keyword)

        # Also capture GPE entities as universities
        for ent in doc.ents:
            if ent.label_ == "GPE":
                education.append(ent.text)

        return list(set(education))

    def _extract_college(self, text: str, doc) -> str | None:
        """
        Extract college/university name from text.

        Uses heuristics: look for university/college keywords followed by names.
        """
        university_patterns = [
            r"(university of [a-zA-Z\s]+)",
            r"([a-zA-Z\s]+university)",
            r"([a-zA-Z\s]+college)",
            r"(institute of [a-zA-Z\s]+)",
            r"([a-zA-Z\s]+institute)",
        ]

        text_lower = text.lower()
        for pattern in university_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_degree(self, text: str, doc) -> str | None:
        """
        Extract degree name (e.g., "Bachelor of Science in Computer Science").
        """
        degree_patterns = [
            r"bachelor of [a-zA-Z\s]+",
            r"master of [a-zA-Z\s]+",
            r"phd in [a-zA-Z\s]+",
            r"b\.s\. in [a-zA-Z\s]+",
            r"m\.s\. in [a-zA-Z\s]+",
            r"m\.b\.a\.",
            r"associate degree",
        ]

        text_lower = text.lower()
        for pattern in degree_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                return match.group(0).title()

        return None

    def _extract_experience_years(self, text: str, doc) -> float:
        """
        Extract experience in years using heuristic patterns.

        Looks for patterns like:
        - "X years of experience"
        - "X years experience"
        - Date ranges (2015-2023)
        """
        experience_years = 0.0
        text_lower = text.lower()

        # Pattern 1: "X years of experience"
        pattern1 = r"(\d+(?:\.\d+)?)\s+years?\s+of\s+experience"
        match = re.search(pattern1, text_lower)
        if match:
            experience_years = max(experience_years, float(match.group(1)))

        # Pattern 2: "X+ years experience"
        pattern2 = r"(\d+(?:\.\d+)?)\s*\+?\s+years?\s+experience"
        match = re.search(pattern2, text_lower)
        if match:
            experience_years = max(experience_years, float(match.group(1)))

        # Pattern 3: Calculate from date ranges (YYYY-YYYY)
        date_pattern = r"(20\d{2})\s*[-–]\s*(20\d{2}|present|current)"
        matches = re.findall(date_pattern, text_lower)
        if matches:
            max_span = 0
            for start, end in matches:
                if end.lower() in {"present", "current"}:
                    span = 2024 - int(start)
                else:
                    span = int(end) - int(start)
                max_span = max(max_span, span)
            experience_years = max(experience_years, float(max_span))

        return experience_years

    def _extract_total_experience_int(self, text: str, doc) -> int:
        """
        Extract total experience as integer for backward compatibility.
        """
        years = self._extract_experience_years(text, doc)
        return int(round(years))
