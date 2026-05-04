# vectorDB.py

import chromadb

from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction
)

# Persistent DB

client = chromadb.PersistentClient(
    path="./chroma_db"
)

# Better + avoids ONNX runtime issues

embedding_function = (
    SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
)

collection = client.get_or_create_collection(
    name="internal_rag",
    embedding_function=embedding_function
)