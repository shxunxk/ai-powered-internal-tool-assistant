from loaders import load_documents
from chunking import chunk_text
from vectorDB import collection

documents = load_documents("./data")

for doc in documents:
    chunks = chunk_text(doc["content"])

    for i, chunk in enumerate(chunks):

        metadata = {
            "source": doc["source"]
        }

        collection.add(
            documents=[chunk],
            metadatas=[metadata],
            ids=[f"{doc['source']}_{i}"]
        )