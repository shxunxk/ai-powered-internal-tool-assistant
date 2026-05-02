from pathlib import Path

def load_text_files(directory):
    documents = []

    for file in Path(directory).rglob("*"):
        if file.suffix in [".md", ".py", ".json", ".yaml", ".yml"]:
            content = file.read_text(errors="ignore")

            documents.append({
                "content": content,
                "source": str(file),
                "language": file.suffix.lstrip("."),
            })

    return documents