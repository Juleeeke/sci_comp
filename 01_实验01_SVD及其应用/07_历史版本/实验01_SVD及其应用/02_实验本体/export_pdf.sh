#!/usr/bin/env bash
set -euo pipefail
experiment_dir="$(cd "$(dirname "$0")/.." && pwd)"
config_dir="$(mktemp -d "${TMPDIR:-/tmp}/sci-pdf.XXXXXX")"
trap 'rm -rf -- "$config_dir"' EXIT
cat > "$config_dir/fonts.conf" <<XML
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig>
<dir>/System/Library/Fonts</dir>
<dir>/System/Library/Fonts/Supplemental</dir>
<dir>/Users/juleyau/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/libreoffice-headless/libreoffice/LibreOfficeDev.app/Contents/Resources/fonts/truetype</dir>
<cachedir>$config_dir/cache</cachedir>
</fontconfig>
XML
FONTCONFIG_FILE="$config_dir/fonts.conf" soffice --headless --convert-to pdf --outdir "$experiment_dir/03_最终实验报告" "$experiment_dir/03_最终实验报告/实验01_SVD及其应用_实验报告.docx"
