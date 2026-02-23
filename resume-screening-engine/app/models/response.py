from pydantic import BaseModel
from typing import List


class RankedResume(BaseModel):
    rank: int
    candidate_name: str
    match_score: float
    strengths: List[str]
    missing_skills: List[str]
    experience_gap: float
    explanation: str


class RankingResponse(BaseModel):
    results: List[RankedResume]
