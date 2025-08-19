#!/usr/bin/env python3
"""
Lê tags_freq.txt (formato: 'tag<TAB>freq') e gera lista_tags_gerada.md.
Aceita separadores por TAB ou múltiplos espaços. Ignora linhas inválidas com aviso.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
freq_file = ROOT / "tags_freq.txt"
out_md = ROOT / "lista_tags_gerada.md"

if not freq_file.exists():
  print(f"⚠️ {freq_file} não encontrado. Nada a fazer.")
  exit(0)

pairs = []
for line in freq_file.read_text(encoding="utf-8", errors="ignore").splitlines():
  raw = line.strip()
  if not raw:
    continue
  # tenta <tag>\t<count>, senão tenta split por whitespace
  tag = None
  count = None
  if "\t" in raw:
    parts = raw.split("\t", 1)
  else:
    parts = raw.rsplit(maxsplit=1)
  if len(parts) == 2:
    tag, cnt_s = parts[0].strip(), parts[1].strip()
    try:
      count = int(cnt_s)
    except Exception:
      print(f"⚠️ Erro ao converter linha: {raw}")
      continue
    pairs.append((tag, count))
  else:
    print(f"⚠️ Linha inválida: {raw}")

# ordena por frequência desc e depois por tag
pairs.sort(key=lambda x: (-x[1], x[0]))

if not pairs:
  print("⚠️ Nenhuma frequência válida encontrada.")
  out_md.write_text("_Sem tags para exibir._\n", encoding="utf-8")
  exit(0)

with out_md.open("w", encoding="utf-8") as fp:
  fp.write("# Tags (lista gerada)\n\n")
  for tag, cnt in pairs:
    fp.write(f"- **{tag}** ({cnt})\n")

print(f"✅ Lista gerada em {out_md}")
