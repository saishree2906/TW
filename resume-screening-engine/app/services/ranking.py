# app/services/ranking.py
from typing import List, Dict
from app.services.scoring import AdvancedScoringEngine

# from app.services.explanation import ExplanationGenerator
from app.services.matching.explanation import ExplanationGenerator
from datetime import datetime


class RankingEngine:
    """
    Deterministic resume ranking with stable sort and tie-breaking.
    Includes logging for ML training data collection.
    """

    def __init__(self):
        self.scoring_engine = AdvancedScoringEngine()
        self.explanation_gen = ExplanationGenerator()
        self.ranking_history = []

    def rank_resumes(self, resumes: List, jd_features: Dict) -> Dict:
        """
        Rank resumes with comprehensive scoring and analysis.

        Returns:
            {
                "results": [RankedResume],
                "metadata": {
                    "total_candidates": int,
                    "timestamp": str,
                    "job_requirements": Dict
                }
            }
        """
        scored_resumes = []

        for resume in resumes:
            # Calculate comprehensive score
            score_result = self.scoring_engine.calculate_match_score(
                resume, jd_features, verbose=True
            )

            # Generate explanation
            explanation_result = self.explanation_gen.generate(
                resume_skills=getattr(resume, "skills", set()),
                required_skills=jd_features.get("required_skills", set()),
                experience_years=getattr(resume, "experience_years", 0),
                min_experience=jd_features.get("min_experience", 2.0),
                match_score=score_result["overall_score"],
                certifications=getattr(resume, "certifications", set()),
                education_level=getattr(resume, "education_level", 0),
            )

            scored_resumes.append(
                {
                    "candidate_name": getattr(
                        resume, "candidate_name", "Unknown"
                    ),
                    "overall_score": score_result["overall_score"],
                    "component_scores": score_result["component_scores"],
                    "confidence": score_result["confidence"],
                    "strengths": explanation_result["strengths"],
                    "weaknesses": explanation_result["weaknesses"],
                    "gaps": explanation_result["gaps"],
                    "missing_skills": explanation_result[
                        "gaps"
                    ],  # gaps contains missing skills
                    "experience_gap": explanation_result["metrics"].get(
                        "experience_gap_years", 0
                    ),
                    "explanation": explanation_result["summary"],
                    "detailed_analysis": explanation_result[
                        "detailed_analysis"
                    ],
                    "readiness": explanation_result["readiness"],
                    "metrics": explanation_result.get("metrics", {}),
                }
            )

        # Sort with stable, deterministic tie-breaking
        ranked = sorted(
            scored_resumes,
            key=lambda x: (
                -x["overall_score"],  # Primary: score (descending)
                -x["component_scores"]["skills"],  # Tie-breaker: skill score
                -x["component_scores"][
                    "experience"
                ],  # Tie-breaker: experience
                x["candidate_name"],  # Tie-breaker: alphabetical
            ),
            reverse=False,
        )

        # Assign final ranks
        final_ranked = []
        for idx, item in enumerate(ranked, start=1):
            item["rank"] = idx
            final_ranked.append(item)

        # Store ranking for ML purposes
        ranking_record = {
            "timestamp": datetime.now().isoformat(),
            "jd_hash": hash(
                str(sorted(jd_features.get("required_skills", [])))
            ),
            "candidates_count": len(resumes),
            "ranked_results": final_ranked,
        }
        self.ranking_history.append(ranking_record)

        return {
            "results": final_ranked,
            "metadata": {
                "total_candidates": len(resumes),
                "timestamp": ranking_record["timestamp"],
                "top_match": (
                    final_ranked[0]["candidate_name"] if final_ranked else None
                ),
                "top_match_score": (
                    final_ranked[0]["overall_score"] if final_ranked else 0
                ),
                "average_score": round(
                    (
                        sum(x["overall_score"] for x in final_ranked)
                        / len(final_ranked)
                        if final_ranked
                        else 0
                    ),
                    2,
                ),
                "job_requirements": {
                    "required_skills": sorted(
                        list(jd_features.get("required_skills", set()))
                    )[:10],
                    "min_experience": jd_features.get("min_experience", 2.0),
                    "min_education": jd_features.get("min_education", 2),
                },
            },
        }


def rank_resumes(resumes, jd_features):
    """Legacy interface for backward compatibility."""
    engine = RankingEngine()
    result = engine.rank_resumes(resumes, jd_features)

    # Flatten for legacy API
    return [
        {
            "rank": r["rank"],
            "candidate_name": r["candidate_name"],
            "match_score": r["overall_score"],
            "strengths": r["strengths"],
            "missing_skills": r["missing_skills"],
            "experience_gap": r["experience_gap"],
            "explanation": r["explanation"],
        }
        for r in result["results"]
    ]
