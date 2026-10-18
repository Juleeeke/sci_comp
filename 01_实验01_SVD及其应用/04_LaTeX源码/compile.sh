#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if command -v tectonic >/dev/null 2>&1; then
  tectonic --keep-logs main.tex
elif [[ -x "${CODEX_TECTONIC_PATH:-}" ]]; then
  "$CODEX_TECTONIC_PATH" --keep-logs main.tex
elif [[ -x /Applications/ChatGPT.app/Contents/Resources/tectonic/tectonic ]]; then
  /Applications/ChatGPT.app/Contents/Resources/tectonic/tectonic --keep-logs main.tex
else
  echo 'Install Tectonic or set CODEX_TECTONIC_PATH.' >&2
  exit 1
fi
cp main.pdf ../03_最终实验报告/SVD_Report_English_LaTeX.pdf
