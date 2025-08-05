from sentence_transformers import SentenceTransformer, util

# Load a pre-trained model. This will be downloaded on the first run.
model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculates the semantic similarity between two texts using a sentence-transformer model.

    Args:
        text1: The first text string.
        text2: The second text string.

    Returns:
        A float between -1 and 1 representing the cosine similarity.
    """
    if not text1 or not text2:
        return 0.0

    try:
        # Generate embeddings for both texts
        embedding1 = model.encode(text1, convert_to_tensor=True)
        embedding2 = model.encode(text2, convert_to_tensor=True)

        # Calculate cosine similarity
        cosine_scores = util.pytorch_cos_sim(embedding1, embedding2)
        return cosine_scores.item()
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return 0.0
