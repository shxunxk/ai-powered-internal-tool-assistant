from pathlib import Path
import json
import yaml

from chunkers import (
    chunk_python,
    chunk_markdown,
    chunk_json,
    yaml_chunk
)

from vectorDB import collection


BASE = Path(__file__).resolve().parents[2]

DATA_DIRS = [

    {
        "path": BASE / "data/code",
        "type": "code"
    },

    {
        "path": BASE / "data/docs",
        "type": "docs"
    },

    {
        "path": BASE / "data/records",
        "type": "records"
    }
]


for data in DATA_DIRS:

    data_dir = data["path"]

    doc_type = data["type"]

    for file in data_dir.rglob("*"):

        if not file.is_file():
            continue

        suffix = file.suffix.lower()

        try:

            with open(
                file,
                "r",
                encoding="utf-8"
            ) as f:

                raw_content = f.read()

        except Exception as e:

            print(
                f"Failed to read {file}: {e}"
            )

            continue

        chunks = []

        # ======================
        # PYTHON
        # ======================

        if suffix == ".py":

            chunks = chunk_python(

                raw_content,

                source=str(file),

                doc_type=doc_type
            )

        # ======================
        # MARKDOWN
        # ======================

        elif suffix == ".md":

            chunks = chunk_markdown(

                raw_content,

                source=str(file),

                doc_type=doc_type
            )

        # ======================
        # YAML
        # ======================

        elif suffix in [".yml", ".yaml"]:

            try:

                parsed_yaml = yaml.safe_load(
                    raw_content
                )

                chunks = yaml_chunk(

                    parsed_yaml,

                    source=str(file),

                    doc_type=doc_type
                )

            except Exception as e:

                print(
                    f"YAML parse error {file}: {e}"
                )

                continue

        # ======================
        # JSON
        # ======================

        elif suffix == ".json":

            try:

                parsed_json = json.loads(
                    raw_content
                )

                chunks = chunk_json(

                    parsed_json,

                    source=str(file),

                    doc_type=doc_type
                )

            except Exception as e:

                print(
                    f"JSON parse error {file}: {e}"
                )

                continue

        else:
            continue

        # ======================
        # STORE
        # ======================

        for idx, chunk in enumerate(chunks):

            collection.add(

                documents=[
                    chunk["content"]
                ],

                metadatas=[
                    chunk["metadata"]
                ],

                ids=[
                    f"{file}_{idx}"
                ]
            )

            print(

                f"Inserted chunk {idx} "
                f"from {file}"
            )

print("\nIngestion Complete")