from pathlib import Path
import json
import argparse
import io
import tempfile
import urllib.error
import urllib.request
import zipfile
from urllib.parse import urlparse
import yaml

from backend.rag.chunkers import (
    chunk_python,
    chunk_markdown,
    chunk_json,
    yaml_chunk
)

from backend.rag.vectorDB import clear_store, generate_embeddings, upsert_vectors

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
    """Download a public GitHub archive and index it without cloning."""
    parsed_url = urlparse(repo_url.strip())
    if parsed_url.netloc.lower() not in {"github.com", "www.github.com"}:
        raise ValueError("repo_url must point to a GitHub repository")

    parts = [part for part in parsed_url.path.split("/") if part]
    if len(parts) != 2:
        raise ValueError("repo_url must look like https://github.com/owner/repository")

    owner, repository = parts
    repository = repository.removesuffix(".git")
    archive_url = f"https://codeload.github.com/{owner}/{repository}/zip/HEAD"

    if replace:
        clear_store()

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            request = urllib.request.Request(
                archive_url,
                headers={"User-Agent": "AI-Internal-Tool-Assistant"},
            )
            with urllib.request.urlopen(request, timeout=60) as response:
                archive = response.read()
        except urllib.error.HTTPError as error:
            raise RuntimeError(f"GitHub archive download failed: HTTP {error.code}") from error
        except urllib.error.URLError as error:
            raise RuntimeError(f"GitHub archive download failed: {error.reason}") from error

        try:
            with zipfile.ZipFile(io.BytesIO(archive)) as archive_file:
                archive_file.extractall(temp_dir)
        except zipfile.BadZipFile as error:
            raise RuntimeError("GitHub returned an invalid repository archive") from error

        extracted_root = next(Path(temp_dir).iterdir(), None)
        if extracted_root is None:
            raise RuntimeError("GitHub repository archive was empty")

        ingest_directory(extracted_root, doc_type="github")


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