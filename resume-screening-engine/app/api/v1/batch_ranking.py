
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
import logging
import tempfile
import os

from app.services.parser.spacy_parser import SpacyResumeParser
from app.services.feature_engine import (
    extract_resume_features,
    extract_jd_features,
)
from app.services.ranking import RankingEngine
from app.services.parser.pii_masker import mask_pii

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/parse/resumes")
async def parse_multiple_resumes(
    files: List[UploadFile] = File(...),
    job_description: str = Form(...),
    role: Optional[str] = Form(default=None),
    min_experience: Optional[float] = Form(default=2.0),
):
    if not files:
        raise HTTPException(status_code=400, detail="No resume files provided")

    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description required")

    resumes = []
    parse_errors = []
    temp_files = []

    try:
        for idx, file in enumerate(files):
            temp_path = None
            try:
                msg = f"Parsing resume {idx + 1}/{len(files)}: {file.filename}"
                logger.info(msg)

                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".pdf"
                ) as tmp:
                    content = await file.read()
                    tmp.write(content)
                    temp_path = tmp.name
                    temp_files.append(temp_path)

                parser = SpacyResumeParser(file_path=temp_path)
                parsed = parser.parse("")

                # Fairness: Mask PII before feature extraction and ranking
                name = parsed.get("name", "Unknown")
                parsed["name"] = "[NAME_REDACTED]"
                if "raw_text" in parsed:
                    parsed["raw_text"] = mask_pii(parsed["raw_text"], name)

                features = extract_resume_features(parsed)
                resumes.append(features)

            except Exception as e:
                logger.error(f"Failed to parse {file.filename}: {str(e)}")
                parse_errors.append(
                    {"filename": file.filename, "error": str(e)}
                )

        if not resumes:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse all resumes. Errors: {parse_errors}",
            )

        jd_features = extract_jd_features(job_description)
        jd_features["min_experience"] = float(min_experience)
        jd_features["role"] = role or "Custom"

        ranking_engine = RankingEngine()
        ranking_result = ranking_engine.rank_resumes(resumes, jd_features)

        return {
            "success": True,
            "ranking_result": ranking_result["results"],
            "metadata": ranking_result["metadata"],
            "parse_errors": parse_errors if parse_errors else None,
        }

    finally:
        for temp_path in temp_files:
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {temp_path}: {e}")
