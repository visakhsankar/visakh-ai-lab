from typing import List

from openai import OpenAI


def generate_answer(client: OpenAI, question: str, retrieved_chunks: List[dict]) -> str:
    """Generate a grounded answer from retrieved chunks using GPT-4o-mini."""
    context = "\n\n".join(
        f"[Chunk {item['chunk_index']}]\n{item['chunk_text']}"
        for item in retrieved_chunks
    )
    prompt = f"""You are answering questions about a document using only the retrieved context below.
If the answer is not contained in the context, say so clearly.

Retrieved Context:
{context}

Question: {question}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Answer only from the provided context."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content
