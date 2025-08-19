#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

: "${CONTENT_DIRS:=posts capitulos}"
export CONTENT_DIRS

python3 scripts/gerar_categories.py || { echo "❌ Falha ao gerar categorias."; exit 1; }
echo "✅ Categorias atualizadas."
