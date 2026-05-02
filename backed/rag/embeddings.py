from sentence_transformers import SentenceTransformer
from vectorDB import collection

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

def embed_text(text):
    return model.encode(text).tolist()