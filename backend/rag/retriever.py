from sentence_transformers import SentenceTransformer, CrossEncoder
from rag.vectorDB import index, generate_embeddings

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def retriever(query, doc_type, top_k=10):

    print("Doc type:", doc_type)

    query_vector = generate_embeddings(query)

    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
        filter={
        "doc_type": {"$eq": doc_type}
        }
    )

    matches = results["matches"]

    print("Matches\n", matches)

    docs = []
    metadatas = []

    for m in matches:
        docs.append(m["metadata"].get("text", ""))
        meta = dict(m["metadata"])
        meta.pop("text", None)
        metadatas.append(meta)

    pairs = [(query, doc) for doc in docs]
    scores = reranker.predict(pairs)

    reranked = sorted(
        zip(docs, metadatas, scores),
        key=lambda x: x[2],
        reverse=True
    )

    return [
        {
            "content": doc,
            "metadata": meta,
        }
        for doc, meta, _ in reranked[:5]
    ]