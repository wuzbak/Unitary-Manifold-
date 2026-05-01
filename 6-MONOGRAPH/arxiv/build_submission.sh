#!/usr/bin/env bash
# build_submission.sh — create the arXiv upload archive for v9.11
# Run from the repo root:  bash arxiv/build_submission.sh
set -e

cd "$(dirname "$0")"   # ensure we are in arxiv/

echo "==> Compiling LaTeX (3 passes)..."
pdflatex -interaction=nonstopmode main.tex
bibtex main || true
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex

echo "==> Creating submission archive..."
tar -czf unitary-manifold-arxiv.tar.gz main.tex references.bib

echo ""
echo "Done!  Upload  arxiv/unitary-manifold-arxiv.tar.gz  to https://arxiv.org/submit"
echo "Do NOT upload the .pdf — arXiv compiles it automatically."
