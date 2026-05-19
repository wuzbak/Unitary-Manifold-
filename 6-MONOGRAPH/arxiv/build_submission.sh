#!/usr/bin/env bash
# build_submission.sh — create the arXiv upload archive for v11.4
# Run from repo root: bash 6-MONOGRAPH/arxiv/build_submission.sh [--dry-run]
set -euo pipefail

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
fi

cd "$(dirname "$0")"   # ensure we are in arxiv/

if [[ "$DRY_RUN" == "true" ]]; then
  echo "==> Dry run: validating required files"
  test -f main.tex
  test -f references.bib
  echo "==> Dry run: would run pdflatex/bibtex and package unitary-manifold-arxiv.tar.gz"
  exit 0
fi

echo "==> Compiling LaTeX (3 passes)..."
pdflatex -interaction=nonstopmode main.tex
bibtex main || true
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex

echo "==> Creating submission archive..."
tar -czf unitary-manifold-arxiv.tar.gz main.tex references.bib

echo ""
echo "Done! Upload 6-MONOGRAPH/arxiv/unitary-manifold-arxiv.tar.gz to https://arxiv.org/submit"
echo "Do NOT upload the .pdf — arXiv compiles it automatically."
