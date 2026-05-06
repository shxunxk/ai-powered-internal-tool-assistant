import ast
import json
import yaml
import uuid
import re


# =========================
# BASE METADATA
# =========================

def build_base_metadata(source, doc_type, language):
    return {
        "source": source,
        "doc_type": doc_type,
        "language": language
    }


def add_chunk_id(metadata):
    metadata["chunk_id"] = str(uuid.uuid4())
    return metadata


import ast
import json
import yaml
import uuid
import re


# =========================
# BASE METADATA
# =========================

def build_base_metadata(source, doc_type, language):
    return {
        "source": source,
        "doc_type": doc_type,
        "language": language
    }


def add_chunk_id(metadata):
    metadata["chunk_id"] = str(uuid.uuid4())
    return metadata


# =========================
# PYTHON CHUNKING
# =========================

def chunk_python(data, source=None, doc_type=None):

    tree = ast.parse(data)
    lines = data.splitlines()

    chunks = []
    used_lines = set()

    for node in ast.walk(tree):

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):

            start = node.lineno
            end = node.end_lineno

            used_lines.update(range(start, end + 1))

            chunk_text = "\n".join(lines[start - 1:end])

            metadata = build_base_metadata(source, doc_type, "python")

            metadata.update({
                "chunk_type": (
                    "function" if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    else "class"
                ),
                "name": node.name,
                "start_line": start,
                "end_line": end,
            })

            chunk_text = chunk_text.strip()

            metadata["text"] = chunk_text
            metadata = add_chunk_id(metadata)

            chunks.append({
                "content": chunk_text,
                "metadata": metadata
            })

    # 🔥 fallback: global code
    remaining = [
        lines[i]
        for i in range(len(lines))
        if (i + 1) not in used_lines
    ]

    if remaining:
        chunk_text = "\n".join(remaining).strip()

        metadata = build_base_metadata(source, doc_type, "python")

        metadata.update({
            "chunk_type": "global_code",
            "text": chunk_text
        })

        metadata = add_chunk_id(metadata)

        chunks.append({
            "content": chunk_text,
            "metadata": metadata
        })

    return chunks


# =========================
# MARKDOWN CHUNKING
# =========================

def chunk_markdown(data, source=None, doc_type=None):

    # better split by headers
    sections = re.split(r"\n(?=#)", data)

    chunks = []

    for idx, section in enumerate(sections):

        section = section.strip()
        if not section:
            continue

        metadata = build_base_metadata(source, doc_type, "markdown")

        metadata.update({
            "chunk_type": "section",
            "section_index": idx,
            "text": section
        })

        metadata = add_chunk_id(metadata)

        chunks.append({
            "content": section,
            "metadata": metadata
        })

    return chunks


# =========================
# YAML CHUNKING
# =========================

def yaml_chunk(parsed, source, doc_type):

    chunks = []

    def flatten(obj, prefix=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                yield from flatten(v, f"{prefix}{k}.")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                yield from flatten(item, f"{prefix}{i}.")
        else:
            yield prefix[:-1], obj

    flat_items = list(flatten(parsed))

    content_lines = [
        f"{key}: {value}"
        for key, value in flat_items
    ]

    chunk_text = "\n".join(content_lines).strip()

    metadata = build_base_metadata(source, doc_type, "yaml")

    metadata.update({
        "chunk_type": "yaml_flat",
        "text": chunk_text
    })

    metadata = add_chunk_id(metadata)

    chunks.append({
        "content": chunk_text,
        "metadata": metadata
    })

    return chunks


# =========================
# JSON CHUNKING (RECURSIVE)
# =========================

def flatten_json(obj, prefix=""):

    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from flatten_json(v, f"{prefix}{k}.")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from flatten_json(v, f"{prefix}{i}.")
    else:
        yield prefix[:-1], obj


def chunk_json(data, source=None, doc_type=None):

    chunks = []

    if isinstance(data, dict):

        for key, value in data.items():

            content = json.dumps({key: value}, indent=2)

            metadata = build_base_metadata(source, doc_type, "json")

            metadata.update({
                "chunk_type": "json_section",
                "section": key,
                "text": content
            })

            metadata = add_chunk_id(metadata)

            chunks.append({
                "content": content,
                "metadata": metadata
            })

    elif isinstance(data, list):

        for idx, item in enumerate(data):

            content = json.dumps(item, indent=2)

            metadata = build_base_metadata(source, doc_type, "json")

            metadata.update({
                "chunk_type": "json_item",
                "index": idx,
                "text": content
            })

            metadata = add_chunk_id(metadata)

            chunks.append({
                "content": content,
                "metadata": metadata
            })

    return chunks