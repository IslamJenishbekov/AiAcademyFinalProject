from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import os
import pickle
from sentence_transformers import CrossEncoder
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
index_path = 'employees_rag/data/index.faiss'
chunks_path = 'employees_rag/data/chunks.pkl'
embedder = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

with open(chunks_path, "rb") as f:
    chunks = pickle.load(f)

# Загружаем FAISS индекс
index = faiss.read_index(index_path)

def get_bot_response(query, top_k=5):
    print("START:")
    q_emb = embedder.encode([query])
    D, I = index.search(np.array(q_emb), k=10)
    candidates = [chunks[idx] for idx in I[0]]

    # 2) CrossEncoder reranking
    pairs = [(query, passage) for passage in candidates]
    scores = cross_encoder.predict(pairs)
    reranked = [c for _, c in sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)]

    # 3) Берем top_k документов
    context = "\n\n".join(reranked[:top_k])

    # 4) LLM (новый API)
    prompt = f"""
    Ты — ассистент сотрудника банка. Используй контекст из внутренних документов для ответа.

    Вопрос: {query}

    Контекст документов:
    {context}

    Ответи понятно и структурированно.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # можно gpt-4o / gpt-4-turbo
        messages=[
            {"role": "system", "content": "Ты помогаешь сотрудникам банка."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content