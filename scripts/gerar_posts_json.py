#!/usr/bin/env python3
import os, re, json
from pathlib import Path

# Raiz do repo (scripts está um nível abaixo)
ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

CONTENT_DIRS = os.environ.get("CONTENT_DIRS", "posts capitulos").split()
OUTPUT = ROOT / "docs" / "posts.json"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

def extract_meta(text: str):
    meta = {}
    # YAML front matter simples
    m = re.search(r"^---\s*(.*?)\s*---", text, flags=re.S | re.M)
    if not m:
        return meta
    block = m.group(1)
    for line in block.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip().lower()
            v = v.strip().strip('"').strip("'")
            meta[k] = v
    return meta

posts = []
for d in CONTENT_DIRS:
    p = Path(d)
    if not p.exists():
        continue
    for f in p.rglob("*"):
        if f.suffix.lower() in (".qmd", ".md"):
            try:
                t = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            meta = extract_meta(t)
            title = meta.get("title")
            if title:
                posts.append({
                    "title": title,
                    "file": f.as_posix(),
                    "date": meta.get("date", ""),
                    "tags": meta.get("tags", ""),
                })

# Ordena por data desc se possível (mantém os sem data no final)
def keyfn(it):
    return it.get("date",""), it.get("title","")
posts_sorted = sorted(posts, key=keyfn, reverse=True)

with OUTPUT.open("w", encoding="utf-8") as fp:
    json.dump(posts_sorted, fp, ensure_ascii=False, indent=2)

print(f"✅ {len(posts_sorted)} posts salvos em {OUTPUT}")
