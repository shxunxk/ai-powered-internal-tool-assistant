import ast
import yaml
import json


def build_base_metadata(
    source,
    doc_type,
    language
):

    return {

        "source": source,

        "doc_type": doc_type,

        "language": language,
    }


# =========================
# PYTHON
# =========================

def chunk_python(
    data,
    source=None,
    doc_type=None
):

    tree = ast.parse(data)

    chunks = []

    lines = data.splitlines()

    for node in ast.walk(tree):

        # FUNCTIONS

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef
            )
        ):

            start = node.lineno
            end = node.end_lineno

            chunk = "\n".join(
                lines[start - 1:end]
            )

            metadata = build_base_metadata(
                source,
                doc_type,
                "python"
            )

            metadata.update({

                "chunk_type": "function",

                "function_name": node.name,

                "start_line": start,

                "end_line": end,
            })

            chunks.append({

                "content": chunk,

                "metadata": metadata
            })

        # CLASSES

        elif isinstance(node, ast.ClassDef):

            start = node.lineno
            end = node.end_lineno

            chunk = "\n".join(
                lines[start - 1:end]
            )

            metadata = build_base_metadata(
                source,
                doc_type,
                "python"
            )

            metadata.update({

                "chunk_type": "class",

                "class_name": node.name,

                "start_line": start,

                "end_line": end,
            })

            chunks.append({

                "content": chunk,

                "metadata": metadata
            })

    return chunks


# =========================
# MARKDOWN
# =========================

def chunk_markdown(
    data,
    source=None,
    doc_type=None
):

    sections = data.split("\n\n")

    chunks = []

    for idx, section in enumerate(sections):

        metadata = build_base_metadata(
            source,
            doc_type,
            "markdown"
        )

        metadata.update({

            "chunk_type": "section",

            "section_index": idx,
        })

        chunks.append({

            "content": section,

            "metadata": metadata
        })

    return chunks


# =========================
# YAML
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
            yield (prefix[:-1], obj)

    flat_items = list(flatten(parsed))

    content_lines = []

    for key, value in flat_items:
        content_lines.append(f"{key}: {value}")

    chunks.append({
        "content": "\n".join(content_lines),
        "metadata": {
            "source": source,
            "type": doc_type,
            "format": "yaml"
        }
    })

    return chunks

# =========================
# JSON
# =========================

def chunk_json(
    data,
    source=None,
    doc_type=None
):

    chunks = []

    if isinstance(data, dict):

        for key, value in data.items():

            metadata = build_base_metadata(
                source,
                doc_type,
                "json"
            )

            metadata.update({

                "chunk_type": "json_section",

                "section": key,
            })

            chunks.append({

                "content": json.dumps(
                    {key: value},
                    indent=2
                ),

                "metadata": metadata
            })

    elif isinstance(data, list):

        for idx, item in enumerate(data):

            metadata = build_base_metadata(
                source,
                doc_type,
                "json"
            )

            metadata.update({

                "chunk_type": "json_item",

                "index": idx,
            })

            chunks.append({

                "content": json.dumps(
                    item,
                    indent=2
                ),

                "metadata": metadata
            })

    return chunks