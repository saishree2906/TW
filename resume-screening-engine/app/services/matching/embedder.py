from sentence_transformers import SentenceTransformer
from typing import List
import threading


class Embedder:
    """
    Thread-safe embedding provider.
    Model is loaded once per process (Uvicorn worker).
    """

    _lock = threading.Lock()
    _model = None

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._load_model()

    def _load_model(self):
        if Embedder._model is None:
            with Embedder._lock:
                if Embedder._model is None:
                    Embedder._model = SentenceTransformer(self.model_name)

    def embed(self, texts: List[str]):
        """
        Generate embeddings for a list of texts.
        Safe to call concurrently.
        """
        return Embedder._model.encode(
            texts, convert_to_tensor=True, normalize_embeddings=True
        )
