from pathlib import Path

root = Path("data")

print(root.rglob("*"))

for file in root.rglob("*"):

    if file.is_file():

        print(file)