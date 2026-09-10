import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"
STORE_DIR = Path(__file__).resolve().parent / "faiss_store"
INDEX_PATH = STORE_DIR / "index.faiss"
METADATA_PATH = STORE_DIR / "metadata.json"

model = SentenceTransformer(MODEL_NAME)


def generate_embeddings(documents):
	"""Generate embeddings for one document or a list of documents."""
	if isinstance(documents, str):
		documents = [documents]

	return model.encode(
		documents,
		convert_to_numpy=True,
		normalize_embeddings=True,
		show_progress_bar=False,
	).astype("float32")


def _load_store():
	if INDEX_PATH.exists() and METADATA_PATH.exists():
		return faiss.read_index(str(INDEX_PATH)), json.loads(
			METADATA_PATH.read_text(encoding="utf-8")
		)

	return faiss.IndexFlatIP(model.get_sentence_embedding_dimension()), []


class FaissIndex:
	def query(self, vector, top_k=10, include_metadata=True, **_):
		index, records = _load_store()
		if index.ntotal == 0:
			return {"matches": []}

		query_vector = np.asarray(vector, dtype="float32")
		if query_vector.ndim == 1:
			query_vector = query_vector.reshape(1, -1)

		scores, positions = index.search(query_vector, min(top_k, index.ntotal))
		matches = []
		for score, position in zip(scores[0], positions[0]):
			if position < 0:
				continue
			record = records[position]
			matches.append({
				"id": record["id"],
				"score": float(score),
				"metadata": record["metadata"] if include_metadata else {},
			})
		return {"matches": matches}


index = FaissIndex()


def upsert_vectors(ids, embeddings, metadatas):
	"""Add vectors and their metadata to the local FAISS store."""
	if not (len(ids) == len(embeddings) == len(metadatas)):
		raise ValueError("ids, embeddings, and metadatas must have equal lengths")

	STORE_DIR.mkdir(parents=True, exist_ok=True)
	faiss_index, records = _load_store()
	vectors = np.asarray(embeddings, dtype="float32")
	if vectors.ndim == 1:
		vectors = vectors.reshape(1, -1)

	faiss.normalize_L2(vectors)
	faiss_index.add(vectors)
	records.extend(
		{"id": item_id, "metadata": metadata}
		for item_id, metadata in zip(ids, metadatas)
	)

	faiss.write_index(faiss_index, str(INDEX_PATH))
	METADATA_PATH.write_text(json.dumps(records), encoding="utf-8")


def clear_store():
	"""Remove the current local index so a repository can be re-ingested."""
	for path in (INDEX_PATH, METADATA_PATH):
		if path.exists():
			path.unlink()