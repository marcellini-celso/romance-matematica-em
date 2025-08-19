#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

: "${CONTENT_DIRS:=posts capitulos}"
export CONTENT_DIRS

python3 scripts/gerar_tags.py || { echo "❌ Falha ao gerar tags."; exit 1; }
python3 scripts/nuvem_tags.py || { echo "❌ Falha ao gerar lista de tags."; exit 1; }

echo "✅ Tags atualizadas."
