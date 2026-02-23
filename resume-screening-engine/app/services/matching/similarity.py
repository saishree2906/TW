import torch


def cosine_similarity(vec1, vec2) -> float:
    """
    Safe cosine similarity between two embedding vectors.
    """

    # Ensure both vectors are 2D tensors
    if vec1.dim() == 1:
        vec1 = vec1.unsqueeze(0)

    if vec2.dim() == 1:
        vec2 = vec2.unsqueeze(0)

    score = torch.nn.functional.cosine_similarity(vec1, vec2, dim=1)
    return float(score.item())
