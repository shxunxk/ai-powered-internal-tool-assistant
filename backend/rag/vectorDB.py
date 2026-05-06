from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX")
CLOUD = os.getenv("PINECONE_CLOUD")
REGION = os.getenv("PINECONE_REGION")

pc = Pinecone(api_key=PINECONE_API_KEY)

# Create index if not exists
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(
            cloud=CLOUD,
            region=REGION
        )
    )

index = pc.Index(INDEX_NAME)

# =========================
# LOAD EMBEDDING MODEL
# =========================

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Embedding model loaded")


# =========================
# EMBEDDING FUNCTION
# =========================

def generate_embeddings(documents):
    embeddings = model.encode(
        documents,
        convert_to_numpy=True,
        show_progress_bar=False
    )
    return embeddings.tolist()


def upsert_vectors(ids, embeddings, metadatas):
    """
    Pinecone upsert format:
    (id, vector, metadata)
    """

    to_upsert = []

    for i in range(len(ids)):
        to_upsert.append(
            (ids[i], embeddings[i], metadatas[i])
        )

    index.upsert(vectors=to_upsert)