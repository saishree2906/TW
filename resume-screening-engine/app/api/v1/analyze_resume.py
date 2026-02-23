from fastapi import APIRouter, UploadFile, File, Form
from app.services.parser.spacy_parser import SpacyResumeParser
from app.services.matching.pipeline import run_matching_pipeline

import tempfile
import shutil
import os

router = APIRouter()


@router.post("/analyze-resume")
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    role: str | None = Form(default=None),
):
    # 1. Save uploaded file to temp path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # 2. Initialize parser with file path (REQUIRED)
        parser = SpacyResumeParser(file_path=tmp_path)

        # 3. Call parse WITH DUMMY ARG (required by signature)
        parsed_resume = parser.parse("")

        # 4. Run matching pipeline
        match_result = run_matching_pipeline(
            resume_data=parsed_resume,
            job_description=job_description,
            role=role,
        )

        return {"parsed_resume": parsed_resume, **match_result}

    finally:
        # 5. Cleanup temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
