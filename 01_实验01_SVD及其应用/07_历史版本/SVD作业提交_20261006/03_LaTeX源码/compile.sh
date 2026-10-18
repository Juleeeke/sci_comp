#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if command -v tectonic >/dev/null 2>&1; then
  tectonic --keep-logs main.tex
elif [[ -x "${CODEX_TECTONIC_PATH:-}" ]]; then
  "$CODEX_TECTONIC_PATH" --keep-logs main.tex
elif [[ -x /Applications/ChatGPT.app/Contents/Resources/tectonic/tectonic ]]; then
  /Applications/ChatGPT.app/Contents/Resources/tectonic/tectonic --keep-logs main.tex
elif command -v xelatex >/dev/null 2>&1; then
  xelatex -interaction=nonstopmode -halt-on-error main.tex
  xelatex -interaction=nonstopmode -halt-on-error main.tex
else
  echo '需要 Tectonic 或 XeLaTeX；也可将本目录上传 Overleaf，选择 XeLaTeX。' >&2
  exit 1
fi
mkdir -p ../00_提交报告
cp main.pdf ../00_提交报告/第一节上机实验_SVD及其应用_实验报告.pdf
