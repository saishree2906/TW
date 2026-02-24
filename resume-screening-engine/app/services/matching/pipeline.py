from typing import Dict
from concurrent.futures import ThreadPoolExecutor

from app.services.matching.embedder import Embedder
from app.services.matching.similarity import cosine_similarity
from app.services.matching.gap_analysis import find_missing_skills
from app.services.matching.explanation import generate_explanation
from app.services.matching.jd_skill_extractor import extract_jd_skills
from app.services.matching.resume_enricher import enrich_resume_text

# Thread pool for CPU-bound embedding work
_executor = ThreadPoolExecutor(max_workers=4)

# Embedder is loaded once per worker
_embedder = Embedder()


def run_matching_pipeline(
    resume_data: Dict, job_description: str, role: str
) -> Dict:
    """
    Phase 3 Pipeline:
    1. Resume text enrichment
    2. Role-aware JD skill extraction
    3. Semantic similarity scoring
    4. Skill gap analysis
    5. Rule-based explanation
    """

    # 1. Enrich resume text for semantic scoring
    resume_text = enrich_resume_text(resume_data)

    # 2. Extract required skills from JD using role
    jd_required_skills = extract_jd_skills(job_description, role)

    # 3. Generate embeddings (offloaded to thread pool)
    future = _executor.submit(_embedder.embed, [resume_text, job_description])

    embeddings = future.result()

    resume_embedding = embeddings[0]
    jd_embedding = embeddings[1]

    match_score = cosine_similarity(resume_embedding, jd_embedding)

    # 4. Gap analysis
    resume_skills = set(resume_data.get("skills", []))
    jd_skills = set(jd_required_skills)

    missing_skills = find_missing_skills(jd_skills, resume_skills)

    # 5. Explanation
    # explanation = generate_explanation(missing_skills, match_score)

    # return {
    #     "match_score": round(match_score, 2),
    #     "jd_required_skills": jd_required_skills,
    #     "missing_keywords": missing_skills,
    #     "explanation": explanation,
    # }
    explanation_results = generate_explanation(
        resume=resume_data,
        jd=jd_required_skills,
        score=match_score
    )

    return {
        "match_score": round(match_score, 2),
        "jd_required_skills": jd_required_skills,
        "missing_keywords": missing_skills,
        **explanation_results  # Unpack strengths, gaps, and readiness
    }