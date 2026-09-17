#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if (( $# == 0 )); then
  set -- example.tex example-color.tex
fi
for source in "$@"; do
  latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error "$source"
done
