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
embedder = SentenceTransformer("deepvk/USER-bge-m3")
cross_encoder = CrossEncoder("DiTy/cross-encoder-russian-msmarco")

with open(chunks_path, "rb") as f:
    chunks = pickle.load(f)

# Загружаем FAISS индекс
index = faiss.read_index(index_path)

def get_bot_response(query, top_k=5):
    q_emb = embedder.encode([query])
    D, I = index.search(np.array(q_emb), k=10)
    candidates = [chunks[idx] for idx in I[0]]

    print("\n\nBiEncoder Results: ")
    for i, text in enumerate(candidates):
        print(f"{i+1} chunk: {text}")
    print('\n\n')
    pairs = [(query, passage) for passage in candidates]
    scores = cross_encoder.predict(pairs)
    reranked = [c for _, c in sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)]

    print("\n\nCrossEncoder Results: ")
    for i, text in enumerate(reranked[:top_k]):
        print(f"{i+1} chunk: {text}")
    print('\n\n')
    # 3) Берем top_k документов
    context = ""
    for i, text in enumerate(reranked[:top_k]):
        context += f"{i+1}-чанк: {text}"

    # 4) LLM (новый API)
    prompt = f"""
    Ты — ассистент сотрудника банка в системе RAG (Retrieval Augmented Generation) 
    Отвечай строго по контексту. Если ответа нет — укажи это. 

    Формат ответа:
    1. Краткий и точный ответ (если есть в контексте).
    2. Если ты не знаешь ответ можешь использовать фразу: "Извините, я не располагаю такой информацией."
    3. Будь вежлив с клиентом, важно клиентоориентированность

    Вопрос: {query}

    Контекст из {top_k} чанков:
    {context}
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
