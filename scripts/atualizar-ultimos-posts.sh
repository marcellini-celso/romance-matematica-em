#!/usr/bin/env bash
set -Eeuo pipefail
umask 002

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

: "${CONTENT_DIRS:=posts capitulos}"
read -r -a CONTENT_ARRAY <<<"$CONTENT_DIRS"

INDEX_FILE="index.qmd"
BEGIN_MARK="<!-- ULTIMOS-POSTS:BEGIN -->"
END_MARK="<!-- ULTIMOS-POSTS:END -->"

echo "🔍 Procurando os 10 itens mais recentes..."
mapfile -t FILES < <(
  for d in "${CONTENT_ARRAY[@]}"; do
    [ -d "$d" ] || continue
    find "$d" -type f \( -name "*.qmd" -o -name "*.md" \) -printf "%T@\t%p\n"
  done | sort -nr | head -n 10 | cut -f2-
)

# Extrai o título do YAML, removendo aspas e espaços ao redor
get_title() {
  awk '
    BEGIN { inmeta=0 }
    /^---[[:space:]]*$/ { inmeta = !inmeta; next }
    inmeta && /^title:[[:space:]]*/ {
      sub(/^title:[[:space:]]*/,""); 
      gsub(/^[[:space:]"'\'']+|[[:space:]"'\'']+$/,""); 
      print; 
      exit
    }
  ' "$1"
}

LISTA=""
for f in "${FILES[@]}"; do
  [ -f "$f" ] || continue
  title="$(get_title "$f")"
  [ -n "$title" ] || title="$(basename "$f")"
  LISTA+="- [${title}](${f})\n"
done

[ -n "$LISTA" ] || { echo "⚠️ Nenhum arquivo encontrado em ${CONTENT_ARRAY[*]}"; exit 0; }

tmp="$(mktemp)"
if grep -q "$BEGIN_MARK" "$INDEX_FILE" 2>/dev/null; then
  awk -v begin="$BEGIN_MARK" -v end="$END_MARK" -v lista="$LISTA" '
    BEGIN{p=0; wrote=0}
    $0~begin {print; print ""; printf "%s", lista; print end; p=1; skip=1; wrote=1; next}
    $0~end && p==1 {skip=0; next}
    skip!=1 {print}
    END{ if(!wrote){ print begin "\n" lista end } }
  ' "$INDEX_FILE" > "$tmp"
else
  {
    cat "$INDEX_FILE" 2>/dev/null || true
    echo
    echo "$BEGIN_MARK"
    echo
    printf "%b" "$LISTA"
    echo
    echo "$END_MARK"
  } > "$tmp"
fi

mv "$tmp" "$INDEX_FILE"
chmod 664 "$INDEX_FILE"

echo "✅ Últimos posts atualizados em $INDEX_FILE"

