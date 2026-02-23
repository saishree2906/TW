from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict

from app.services.matching.pipeline import run_matching_pipeline

router = APIRouter()


class MatchCandidateRequest(BaseModel):
    resume_data: Dict
    job_description: str
    role: str


@router.post("/match-candidate")
async def match_candidate(payload: MatchCandidateRequest):
    try:
        result = run_matching_pipeline(
            resume_data=payload.resume_data,
            job_description=payload.job_description,
            role=payload.role,
        )
        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Matching failed: {str(exc)}"
        )
