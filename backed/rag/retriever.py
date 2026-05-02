from re import T
from vectorDB import collection
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def retriever(query, types, subtype, formt):
    results = collection.query(
        query_texts=[query],
        n_results=20,
        where={
            "type": {"$in": [types]},
            "subtype": {"$in": [subtype]},
            "format": {"$in": [formt]}
        }
    )

    docs = results["documents"][0]
    metadatas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]

    # Build rerank input
    pairs = [(query, doc) for doc in docs]

    scores = reranker.predict(pairs)

    reranked = sorted(
        zip(docs, metadatas, ids, scores),
        key=lambda x: x[3],
        reverse=True
    )

    top_docs = [
        {
            "text": doc,
            "metadata": meta,
            "id": doc_id,
            "score": score
        }
        for doc, meta, doc_id, score in reranked[:5]
    ]

    return top_docs

# def retrieve_docs(query, subtype, format):
#     results = collection.query(
#         query_texts=[query],
#         n_results=5
#         where={
#             "type": {
#                 "$in": ["doc", "docs", "document", "documents"]
#             }
#             subtype: {
#                 "$in": ["log", "logs"]
#             }
#             format: {
#                 "$in": ["json"]
#             }
#         }
#     )
#     return results