import os
from pathlib import Path

home = Path.home()
print("Home:", home)
for p in [".cache", ".modelscope", ".ollama"]:
    target = home / p
    if target.exists():
        count = sum(1 for _ in target.iterdir())
        print(f"{p} exists, top-level items: {count}")
    else:
        print(f"{p} does not exist")
