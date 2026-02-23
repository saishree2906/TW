# app/models/resume.py
from pydantic import BaseModel
from typing import Set, Optional


class ResumeFeatures(BaseModel):
    candidate_name: str
    skills: Set[str]
    experience_years: float
    education_level: int  # 0: None, 1: HS, 2: Bachelor, 3: Master, 4: PhD
    certifications: Set[str] = set()
    keywords: Set[str] = set()
    languages: Set[str] = set()
    email: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
