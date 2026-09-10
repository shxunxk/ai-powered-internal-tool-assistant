from pathlib import Path
import json
import argparse
import subprocess
import tempfile
import yaml

from chunkers import (
    chunk_python,
    chunk_markdown,
    chunk_json,
    yaml_chunk
)

from vectorDB import clear_store, generate_embeddings, upsert_vectors

BASE = Path(__file__).resolve().parents[2]

DATA_DIRS = [
    {"path": BASE / "data/code", "type": "code"},
    {"path": BASE / "data/docs", "type": "docs"},
    {"path": BASE / "data/records", "type": "records"},
]

SUPPORTED_SUFFIXES = {".py", ".md", ".yml", ".yaml", ".json", ".js", ".jsx", ".ts", ".tsx"}


def safe_read(file):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"❌ Failed to read {file}: {e}")
        return None


def ingest_directory(data_dir, doc_type="github"):
    """Chunk and add supported text files from a directory to FAISS."""
    for file in data_dir.rglob("*"):
        if not file.is_file() or ".git" in file.parts or file.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue

        raw_content = safe_read(file)
        if not raw_content:
            continue

        suffix = file.suffix.lower()
        try:
            if suffix == ".py":
                chunks = chunk_python(raw_content, str(file), doc_type)
            elif suffix == ".md":
                chunks = chunk_markdown(raw_content, str(file), doc_type)
            elif suffix in {".yml", ".yaml"}:
                chunks = yaml_chunk(yaml.safe_load(raw_content), str(file), doc_type)
            elif suffix == ".json":
                chunks = chunk_json(json.loads(raw_content), str(file), doc_type)
            else:
                chunks = chunk_markdown(raw_content, str(file), doc_type)
        except Exception as error:
            print(f"Skipping {file}: {error}")
            continue

        if not chunks:
            continue

        documents = [chunk["content"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        ids = [f"{file}_{index}" for index in range(len(chunks))]
        upsert_vectors(ids, generate_embeddings(documents), metadatas)
        print(f"Indexed {file} ({len(chunks)} chunks)")


def ingest_github_repository(repo_url, replace=True):
    """Clone a public GitHub repository and index its supported files."""
    if "github.com" not in repo_url:
        raise ValueError("repo_url must point to a GitHub repository")

    if replace:
        clear_store()

    with tempfile.TemporaryDirectory() as temp_dir:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, temp_dir],
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or "Git clone failed")
        ingest_directory(Path(temp_dir), doc_type="github")


def ingest_local_data():
    for data in DATA_DIRS:

        print(f"\n📦 Processing: {data['type']}")

        data_dir = data["path"]
        doc_type = data["type"]

        if not data_dir.exists():
            print(f"⚠️ Missing dir: {data_dir}")
            continue

        ingest_directory(data_dir, doc_type)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Index local data or a GitHub repository into FAISS")
	parser.add_argument("--repo-url", help="Public GitHub repository URL")
	parser.add_argument("--append", action="store_true", help="Append instead of replacing the current index")
	args = parser.parse_args()

	if args.repo_url:
		ingest_github_repository(args.repo_url, replace=not args.append)
	else:
		ingest_local_data()

	print("\n🎉 Ingestion Complete")