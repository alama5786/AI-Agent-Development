"""
similarity.py  --  measures how "close" two embedding vectors are.

Significance:
    In RAG, text is converted to vectors (embeddings). Texts with similar meaning
    end up with vectors pointing in a similar direction, so cosine similarity
    (1 = same direction, 0 = unrelated, -1 = opposite) lets us rank documents
    by relevance to a question.
"""
import numpy as np

def cosine_similarity(vec1, vec2):
    """
    Calculate the cosine similarity between two vectors.

    Parameters:
    vec1 (numpy.ndarray): First vector.
    vec2 (numpy.ndarray): Second vector.

    Returns:
    float: Cosine similarity between vec1 and vec2.
    """
    # Convert plain Python lists to numpy arrays so we can do vector math.
    v1 = np.array(vec1)
    v2 = np.array(vec2)

    # Formula: cos(theta) = (v1 . v2) / (|v1| * |v2|)
    dot_product = np.dot(v1, v2)
    norm_vec1 = np.linalg.norm(v1)
    norm_vec2 = np.linalg.norm(v2)

    if norm_vec1 == 0 or norm_vec2 == 0:
        return 0.0  # Avoid division by zero

    return dot_product / (norm_vec1 * norm_vec2)
