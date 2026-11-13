#!/bin/bash
cd "$(git rev-parse --show-toplevel)" || exit 1
OUT="tests/evidence/raw_tests.tsv"
echo -e "path\tfilename\tdate\tsize_kb\tin_test_map" > "$OUT"
for dir in tests/evidence tests/rate_limit tests/coverage tests/legacy_test001 .github/workflows results app/market/test001; do
  [ -d "$dir" ] || continue
  find "$dir" -type f 2>/dev/null | grep -v __pycache__ | grep -v ".bak-" | sort | while read f; do
    filename=$(basename "$f")
    date=$(echo "$filename" | grep -oE "[0-9]{4}-[0-9]{2}-[0-9]{2}" | head -1)
    [ -z "$date" ] && date="no-date"
    size=$(du -k "$f" 2>/dev/null | cut -f1)
    if grep -qF "$filename" tests/TEST_MAP_v3.4_FINAL.md 2>/dev/null; then inmap="YES"; else inmap="NO"; fi
    echo -e "$f\t$filename\t$date\t${size}\t$inmap"
  done
done >> "$OUT"
echo "done: $OUT"
tail -n +2 "$OUT" | wc -l
