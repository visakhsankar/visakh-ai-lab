from typing import List, Tuple

import faiss
import numpy as np
from openai import OpenAI

from .embedder import get_embeddings


def build_index(client: OpenAI, chunks: List[str]) -> Tuple[faiss.IndexFlatL2, np.ndarray]:
    """Embed all chunks and load them into a FAISS flat L2 index."""
    embeddings = get_embeddings(client, chunks)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index, embeddings


def retrieve_chunks(
    client: OpenAI,
    question: str,
    chunks: List[str],
    index: faiss.IndexFlatL2,
    top_k: int = 3,
) -> List[dict]:
    """Retrieve the top-k most relevant chunks for a question."""
    q_vec = get_embeddings(client, [question])
    distances, indices = index.search(q_vec, min(top_k, index.ntotal))

    results = []
    for rank, idx in enumerate(indices[0]):
        if idx < len(chunks):
            dist = float(distances[0][rank])
            results.append({
                "rank": rank + 1,
                "chunk_index": int(idx),
                "chunk_text": chunks[idx],
                "distance": dist,
                # Normalise L2 distance to a 0-1 relevance score
                "similarity": round(1 / (1 + dist), 4),
            })
    return results
