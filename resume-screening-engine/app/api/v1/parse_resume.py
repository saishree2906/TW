from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
from uuid import uuid4

from app.services.parser.spacy_parser import SpacyResumeParser
from app.services.parser.normalizer import normalize
from app.core.config import settings

router = APIRouter(prefix="/parse", tags=["Resume Parsing"])

UPLOAD_DIR = settings.UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/resume")
def parse_resume(file: UploadFile = File(...)):
    """
    Parse a resume file and extract structured information.

    Supported formats: PDF, DOCX

    Returns:
        {
            "status": "success",
            "data": {
                "skills": [...],
                "experience_years": <float>,
                "education": [...],
                "contact": {"masked": true}
            }
        }
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    extension = os.path.splitext(file.filename)[1].lower()
    if extension not in {".pdf", ".docx"}:
        raise HTTPException(
            status_code=400, detail="Only PDF and DOCX resumes are supported"
        )

    # Create a temporary file for parsing
    file_id = f"{uuid4()}{extension}"
    file_path = os.path.join(UPLOAD_DIR, file_id)

    try:
        # Save uploaded file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Parse with SpaCy-based parser
        parser = SpacyResumeParser(file_path)
        parsed_data = parser.parse("")

        # Normalize and mask PII
        return normalize(parsed_data)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")

    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)
