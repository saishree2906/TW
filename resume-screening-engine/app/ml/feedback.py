"""
ML Feedback Collection and Model Training Infrastructure

Collects user feedback on rankings for future model improvement.
Stores data for offline ML model retraining.
"""

import json
import os
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class FeedbackCollector:
    """
    Collect user feedback on rankings for future model training.
    Stores data for offline ML model improvement.
    """

    def __init__(self, storage_path: str = "ml_data/feedback"):
        self.storage_path = storage_path
        self._ensure_path()

    def _ensure_path(self):
        """Create storage directory if needed."""
        os.makedirs(self.storage_path, exist_ok=True)

    def collect_feedback(
        self,
        job_description: str,
        candidates: List[Dict],
        user_ranking: List[str],
        selected_candidate: str = None,
        notes: str = None,
    ) -> Dict:
        """
        Store feedback for ML training.

        Args:
            job_description: JD text
            candidates: List of candidate dicts with scores
            user_ranking: Actual ranking by recruiter/hiring manager
            selected_candidate: Final hired candidate
            notes: Additional feedback
        """
        feedback = {
            "timestamp": datetime.now().isoformat(),
            "job_description": job_description,
            "ai_ranking": [
                c.get("candidate_name", str(i))
                for i, c in enumerate(candidates)
            ],
            "user_ranking": user_ranking,
            "selected_candidate": selected_candidate,
            "agreement": self._calculate_agreement(
                [
                    c.get("candidate_name", str(i))
                    for i, c in enumerate(candidates)
                ],
                user_ranking,
            ),
            "notes": notes,
            "scores": {
                c.get("candidate_name", str(i)): c.get("overall_score", 0)
                for i, c in enumerate(candidates)
            },
        }

        # Store as JSON for training
        filename = (
            f"{self.storage_path}/feedback_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(filename, "w") as f:
            json.dump(feedback, f, indent=2)

        logger.info(f"Feedback stored: {filename}")
        return feedback

    def _calculate_agreement(
        self, ai_ranking: List[str], user_ranking: List[str]
    ) -> float:
        """
        Calculate agreement between AI and user ranking.
        Returns score 0-1.
        """
        if not ai_ranking or not user_ranking:
            return 0.0

        agreement = 0
        for i, candidate in enumerate(user_ranking[:5]):
            if candidate in ai_ranking:
                ai_pos = ai_ranking.index(candidate)
                # Closer position = better
                agreement += max(0, 5 - abs(i - ai_pos))

        return min(agreement / 25, 1.0)

    def load_feedback_batch(self, limit: int = 100) -> List[Dict]:
        """Load feedback for ML training."""
        feedbacks = []
        if not os.path.exists(self.storage_path):
            return feedbacks

        files = sorted(os.listdir(self.storage_path))[-limit:]

        for filename in files:
            try:
                with open(os.path.join(self.storage_path, filename)) as f:
                    feedbacks.append(json.load(f))
            except Exception as e:
                logger.warning(f"Failed to load {filename}: {e}")

        return feedbacks


class MLModelTrainer:
    """
    Basic ML training from collected feedback.
    Adapts weights based on feedback accuracy.
    """

    def __init__(self):
        self.feedback_collector = FeedbackCollector()
        self.weights = {
            "skill_weight": 0.40,
            "experience_weight": 0.25,
            "education_weight": 0.15,
            "keyword_weight": 0.20,
        }

    def retrain_from_feedback(self):
        """Retrain weights based on collected feedback."""
        feedbacks = self.feedback_collector.load_feedback_batch()

        if not feedbacks:
            logger.info("No feedback available for retraining")
            return

        logger.info(f"Retraining from {len(feedbacks)} feedback samples")

        # Simple averaging of agreement scores
        agreements = [f.get("agreement", 0) for f in feedbacks]
        avg_agreement = sum(agreements) / len(agreements) if agreements else 0

        # Adjust weights based on overall agreement
        if avg_agreement > 0.7:
            logger.info(
                f"High agreement ({avg_agreement:.2f}). Keeping current weights."
            )
        elif avg_agreement > 0.5:
            logger.info(
                f"Moderate agreement ({avg_agreement:.2f}). Minor adjustments."
            )
            self.weights["skill_weight"] = 0.42
            self.weights["experience_weight"] = 0.26
        else:
            logger.info(
                f"Low agreement ({avg_agreement:.2f}). Significant retraining needed."
            )
            # Could implement more sophisticated retraining here

        logger.info(f"Updated weights: {self.weights}")

    def export_model(self, path: str = "ml_data/model_weights.json"):
        """Export learned weights."""
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "weights": self.weights,
                    "version": "1.0",
                },
                f,
                indent=2,
            )
        logger.info(f"Model exported to {path}")
