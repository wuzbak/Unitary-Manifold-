#!/bin/bash
# Apply all numeric substitutions across all relevant files

# List of files to process (excluding REVIEW_CONCLUSION.md which needs special handling)
FILES=$(grep -rl "14109\|14,109\|14122\|14,122\|12533\|12,533\|11450\|11,450\|11461\|11,461\|12545\|12,545" --include="*.md" --include="*.txt" --include="*.py" --include="*.yml" --include="*.json" . | grep -v ".git" | grep -v "REVIEW_CONCLUSION.md")

for f in $FILES; do
  # Total passing: 14,109 → 14,183
  sed -i 's/14,109/14,183/g' "$f"
  sed -i 's/14109/14183/g' "$f"
  # Total collected: 14,122 → 14,195
  sed -i 's/14,122/14,195/g' "$f"
  sed -i 's/14122/14195/g' "$f"
  # tests/ passing: 12,533 → 12,601
  sed -i 's/~12,533/~12,601/g' "$f"
  sed -i 's/12,533/12,601/g' "$f"
  sed -i 's/12533/12601/g' "$f"
  # tests/ collected: 12,545 → 12,613
  sed -i 's/12,545/12,613/g' "$f"
  sed -i 's/12545/12613/g' "$f"
  # old tests/ count: 11,450 → 12,601
  sed -i 's/11,450/12,601/g' "$f"
  sed -i 's/11450/12601/g' "$f"
  # old tests/ collected: 11,461 → 12,613
  sed -i 's/11,461/12,613/g' "$f"
  sed -i 's/11461/12613/g' "$f"
  # test file count
  sed -i 's/127 test files/145 test files/g' "$f"
  sed -i 's/126 test files/145 test files/g' "$f"
done

echo "Done processing $FILES"
