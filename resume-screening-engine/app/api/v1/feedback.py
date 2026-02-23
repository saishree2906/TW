"""
Feedback endpoint for collecting ranking feedback.

API: POST /api/v1/feedback
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.ml.feedback import FeedbackCollector
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class FeedbackRequest(BaseModel):
    """Feedback submission model."""

    job_description: str
    candidates: List[dict]
    user_ranking: List[str]
    selected_candidate: Optional[str] = None
    notes: Optional[str] = None


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback on ranking accuracy.

    This data is collected for ML model retraining to improve
    future ranking accuracy.
    """
    try:
        collector = FeedbackCollector()
        feedback = collector.collect_feedback(
            job_description=request.job_description,
            candidates=request.candidates,
            user_ranking=request.user_ranking,
            selected_candidate=request.selected_candidate,
            notes=request.notes,
        )

        return {
            "success": True,
            "message": "Feedback recorded successfully",
            "agreement_score": feedback.get("agreement", 0),
            "timestamp": feedback.get("timestamp"),
        }

    except Exception as e:
        logger.error(f"Failed to record feedback: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to record feedback"
        )
