from sentence_transformers import SentenceTransformer, CrossEncoder
from vectorDB import index, generate_embeddings

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def retriever(query, doc_type, top_k=20):
    # =========================
    # 1. Create query embedding
    # =========================
    query_vector = generate_embeddings.encode(query).tolist()

    # =========================
    # 2. Query Pinecone
    # =========================
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
        filter={
        "type": {"$eq": doc_type}
        }
    )

    matches = results["matches"]

    docs = []
    metadatas = []
    ids = []

    for m in matches:
        docs.append(m["metadata"].get("text", ""))
        metadatas.append(m["metadata"])
        ids.append(m["id"])

    # =========================
    # 3. Cross-Encoder rerank
    # =========================
    pairs = [(query, doc) for doc in docs]
    scores = reranker.predict(pairs)

    reranked = sorted(
        zip(docs, metadatas, ids, scores),
        key=lambda x: x[3],
        reverse=True
    )

    # =========================
    # 4. Top results
    # =========================
    return [
        {
            "text": doc,
            "metadata": meta,
            "id": doc_id,
            "score": score
        }
        for doc, meta, doc_id, score in reranked[:5]
    ]