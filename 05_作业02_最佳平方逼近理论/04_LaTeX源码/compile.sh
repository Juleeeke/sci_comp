#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if command -v tectonic >/dev/null 2>&1; then
  tectonic --keep-logs main.tex
elif [[ -x /Applications/ChatGPT.app/Contents/Resources/tectonic/tectonic ]]; then
  compiler=/Applications/ChatGPT.app/Contents/Resources/tectonic/tectonic
  codex_cache="$HOME/Library/Application Support/ChatGPT/latex/tectonic"
  if [[ -d "$codex_cache" ]]; then
    TECTONIC_CACHE_DIR="$codex_cache" "$compiler" --only-cached --keep-logs main.tex
  else
    "$compiler" --keep-logs main.tex
  fi
else
  printf 'Open main.tex in the Codex LaTeX editor or compile it with a local TeX distribution.\n' >&2
  exit 1
fi
