from typing import List

import numpy as np
from openai import OpenAI


def get_embeddings(client: OpenAI, texts: List[str]) -> np.ndarray:
    """Embed a list of texts using OpenAI text-embedding-3-small."""
    response = client.embeddings.create(model="text-embedding-3-small", input=texts)
    return np.array([item.embedding for item in response.data], dtype="float32")
