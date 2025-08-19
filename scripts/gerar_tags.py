#!/usr/bin/env python3
"""
Gera tags.qmd e tags_freq.txt a partir do YAML dos arquivos .qmd/.md.
Sem dependências externas. Suporta:
- tags: [a, b, "c d"]
- tags: "a, b, c"
- tags:
    - a
    - b c
Pastas lidas por padrão: "posts" e "capitulos" (pode sobrescrever via CONTENT_DIRS).
"""
import os, re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

CONTENT_DIRS = os.environ.get("CONTENT_DIRS", "posts capitulos").split()

YAML_RE = re.compile(r"^---\s*\n(.*?)\n---", re.S|re.M)
KEY_RE  = re.compile(r"^\s*([A-Za-z0-9_\-]+)\s*:\s*(.*)$")

def iter_content_files(dirs):
    for d in dirs:
        p = Path(d)
        if not p.exists():
            continue
        for f in p.rglob("*"):
            if f.suffix.lower() in (".qmd", ".md"):
                yield f

def get_yaml_block(text):
    m = YAML_RE.search(text)
    return m.group(1) if m else ""

def split_inline_list(inner: str):
    """Divide 'a, "b c", d' respeitando aspas simples/duplas."""
    items = []
    buf = []
    quote = None
    i = 0
    while i < len(inner):
        ch = inner[i]
        if quote:
            if ch == quote:
                quote = None
            elif ch == '\\' and i+1 < len(inner):
                # mantém caractere escapado
                buf.append(inner[i+1])
                i += 1
            else:
                buf.append(ch)
        else:
            if ch in ('"', "'"):
                quote = ch
            elif ch == ',':
                item = ''.join(buf).strip()
                if item:
                    items.append(item)
                buf = []
            else:
                buf.append(ch)
        i += 1
    # último item
    item = ''.join(buf).strip()
    if item:
        items.append(item)
    # limpa aspas periféricas remanescentes
    return [x.strip().strip('"').strip("'") for x in items if x.strip()]

def parse_tags_from_yaml(yaml_text):
    if not yaml_text:
        return []
    lines = yaml_text.splitlines()
    tags = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = KEY_RE.match(line)
        if m and m.group(1).lower() == "tags":
            rest = m.group(2).strip()
            # Caso 1: lista inline [ ... ]
            if rest.startswith('[') and rest.endswith(']'):
                inner = rest[1:-1].strip()
                tags.extend(split_inline_list(inner))
                i += 1
                continue
            # Caso 2: string "a, b, c"
            if rest:
                tags.extend([x.strip().strip('"').strip("'") for x in rest.split(',') if x.strip()])
                i += 1
                continue
            # Caso 3: lista em bloco com "- item"
            base_indent = len(line) - len(line.lstrip(" "))
            j = i + 1
            while j < len(lines):
                l2 = lines[j]
                if l2.strip().startswith("-"):
                    val = l2.split("-", 1)[1].strip().strip('"').strip("'")
                    if val:
                        tags.append(val)
                    j += 1
                else:
                    m2 = KEY_RE.match(l2)
                    curr_indent = len(l2) - len(l2.lstrip(" "))
                    if m2 and curr_indent <= base_indent:
                        break
                    j += 1
            i = j
            continue
        i += 1
    return [t for t in tags if t]

def normalize_tag(s):
    return s.strip().strip("[]")

all_tags = []
for f in iter_content_files(CONTENT_DIRS):
    try:
        text = f.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    yaml_block = get_yaml_block(text)
    tags = [normalize_tag(t) for t in parse_tags_from_yaml(yaml_block)]
    all_tags.extend(tags)

freq = Counter(all_tags)

# Saídas
freq_path = ROOT / "tags_freq.txt"
tags_qmd_path = ROOT / "tags.qmd"

with freq_path.open("w", encoding="utf-8") as fp:
    for tag, cnt in freq.most_common():
        fp.write(f"{tag}\t{cnt}\n")

with tags_qmd_path.open("w", encoding="utf-8") as fp:
    fp.write('---\ntitle: "Tags"\ndescription: "Índice de tags do site com contagens."\ndate: 2025-08-18\ncategories: [navegação]\npage-layout: full\nformat:\n  html:\n    toc: true\n---\n\n')
    fp.write("# Tags\n\n")
    if not freq:
        fp.write("_Nenhuma tag encontrada._\n")
    else:
        for tag, cnt in freq.most_common():
            fp.write(f"- **{tag}** ({cnt})\n")

print(f"✅ {len(freq)} tags únicas encontradas. Arquivos gerados: {tags_qmd_path}, {freq_path}")
