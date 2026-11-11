import re, sys

PATH = "docs/B_items/Item_12_Part1_SQLite_Architecture.md"
FIELDS = ["job_id", "job_type", "status", "request_id", "user_id", "message_id", "record_type", "priority", "reservation_id", "token_key", "chunk_message_id"]

try:
    with open(PATH, "r", encoding="utf-8", newline="") as f:
        lines = f.readlines()
except FileNotFoundError:
    print("[ABORT] File not found: " + PATH)
    sys.exit(1)

modified = 0
new_lines = []
for line in lines:
    for field in FIELDS:
        pattern = r'(`?' + re.escape(field) + r'`?\s*\([^)]*?)(\))'
        m = re.search(pattern, line)
        if m and "NOT NULL" not in m.group(1):
            line = re.sub(pattern, r'\1, NOT NULL\2', line)
            modified += 1
    if "chunk_index >= 0" in line and "chunk_index IS NOT NULL AND chunk_index >= 0" not in line:
        line = line.replace("chunk_index >= 0", "chunk_index IS NOT NULL AND chunk_index >= 0")
        modified += 1
    new_lines.append(line)

if modified > 0:
    with open(PATH, "w", encoding="utf-8", newline="") as f:
        f.writelines(new_lines)
    print("[OK] " + str(modified) + " changes applied.")
else:
    print("[SKIP] No changes needed.")
