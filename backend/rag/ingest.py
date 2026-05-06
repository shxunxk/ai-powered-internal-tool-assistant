from pathlib import Path
import json
import yaml
import time

from chunkers import (
    chunk_python,
    chunk_markdown,
    chunk_json,
    yaml_chunk
)

from vectorDB import generate_embeddings, upsert_vectors

BASE = Path(__file__).resolve().parents[2]

DATA_DIRS = [
    {"path": BASE / "data/code", "type": "code"},
    {"path": BASE / "data/docs", "type": "docs"},
    {"path": BASE / "data/records", "type": "records"},
]


def safe_read(file):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"❌ Failed to read {file}: {e}")
        return None


for data in DATA_DIRS:

    print(f"\n📦 Processing: {data['type']}")

    data_dir = data["path"]
    doc_type = data["type"]

    if not data_dir.exists():
        print(f"⚠️ Missing dir: {data_dir}")
        continue

    for file in data_dir.rglob("*"):

        if not file.is_file():
            continue

        raw_content = safe_read(file)
        if not raw_content:
            continue

        suffix = file.suffix.lower()
        chunks = []

        try:
            if suffix == ".py":
                chunks = chunk_python(raw_content, str(file), doc_type)

            elif suffix == ".md":
                chunks = chunk_markdown(raw_content, str(file), doc_type)

            elif suffix in [".yml", ".yaml"]:
                parsed = yaml.safe_load(raw_content)
                chunks = yaml_chunk(parsed, str(file), doc_type)

            elif suffix == ".json":
                parsed = json.loads(raw_content)
                chunks = chunk_json(parsed, str(file), doc_type)

            else:
                continue

        except Exception as e:
            print(f"❌ Chunking failed {file}: {e}")
            continue

        if not chunks:
            continue

        print(f"📄 {file} -> {len(chunks)} chunks")

        documents = []
        metadatas = []
        ids = []

        for idx,chunk in enumerate(chunks):
            documents.append(chunk["content"])
            metadatas.append(chunk["metadata"])
            ids.append(f"{file}_{idx}")

        try:
            print("⚡ Generating embeddings...")

            embeddings = generate_embeddings(documents)

            print("⚡ Uploading to Pinecone...")

            upsert_vectors(ids, embeddings, metadatas)

            print("✅ Uploaded successfully")

        except Exception as e:
            print(f"❌ Pinecone insert failed: {e}")

        time.sleep(0.1)

print("\n🎉 Ingestion Complete")