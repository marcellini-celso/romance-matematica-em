#!/usr/bin/env python3
"""
Gera categories.qmd e categories_freq.txt a partir do YAML dos arquivos .qmd/.md.
Sem dependências externas. Suporta:
- categories: [a, b, "c d"]
- categories: "a, b, c"
- categories:
    - a
    - b c
Pastas lidas por padrão: "posts" e "capitulos" (pode sobrescrever via CONTENT_DIRS).
"""
import os, re
from pathlib import Path
from collections import Counter
from datetime import date

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
    item = ''.join(buf).strip()
    if item:
        items.append(item)
    return [x.strip().strip('"').strip("'") for x in items if x.strip()]

def parse_list_from_yaml(yaml_text, key_name="categories"):
    if not yaml_text:
        return []
    lines = yaml_text.splitlines()
    out = []
    i = 0
    key_name = key_name.lower()
    while i < len(lines):
        line = lines[i]
        m = KEY_RE.match(line)
        if m and m.group(1).lower() == key_name:
            rest = m.group(2).strip()
            if rest.startswith('[') and rest.endswith(']'):
                inner = rest[1:-1].strip()
                out.extend(split_inline_list(inner))
                i += 1
                continue
            if rest:
                out.extend([x.strip().strip('"').strip("'") for x in rest.split(',') if x.strip()])
                i += 1
                continue
            base_indent = len(line) - len(line.lstrip(" "))
            j = i + 1
            while j < len(lines):
                l2 = lines[j]
                if l2.strip().startswith("-"):
                    val = l2.split("-", 1)[1].strip().strip('"').strip("'")
                    if val:
                        out.append(val)
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
    return [t for t in out if t]

def normalize(s):
    return s.strip().strip("[]")

all_items = []
for f in iter_content_files(CONTENT_DIRS):
    try:
        text = f.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    yaml_block = get_yaml_block(text)
    items = [normalize(t) for t in parse_list_from_yaml(yaml_block, "categories")]
    all_items.extend(items)

from collections import Counter
freq = Counter(all_items)

freq_path = ROOT / "categories_freq.txt"
qmd_path = ROOT / "categories.qmd"

yaml_header = f"""---
title: "Categorias"
description: "Índice de categorias do site."
date: {date.today()}
categories: [navegação]
page-layout: full
format:
  html:
    toc: true
---

"""

with freq_path.open("w", encoding="utf-8") as fp:
    for item, cnt in freq.most_common():
        fp.write(f"{item}\t{cnt}\n")

with qmd_path.open("w", encoding="utf-8") as fp:
    fp.write(yaml_header)
    fp.write("# Categorias\n\n")
    if not freq:
        fp.write("_Nenhuma categoria encontrada._\n")
    else:
        for item, cnt in freq.most_common():
            fp.write(f"- **{item}** ({cnt})\n")

print(f"✅ {len(freq)} categorias únicas encontradas. Arquivos gerados: {qmd_path}, {freq_path}")
