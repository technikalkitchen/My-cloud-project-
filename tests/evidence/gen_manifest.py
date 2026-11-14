#!/usr/bin/env python3
"""gen_manifest.py v2 — Approved Tests Registry.

Reads approved_tests.tsv, validates 7-field JSONs, builds MANIFEST.md.
Exit code 1 if any errors (for CI/automation).
"""
import os
import sys
import json
import datetime

EVIDENCE = "tests/evidence"
APPROVED = "tests/evidence/approved_tests.tsv"
PENDING = "tests/evidence/pending_tests.tsv"
OUT = "docs/MANIFEST.md"

ITEMS = {
    "01": "Exchanges",       "02": "Aggregators",     "03": "Universe",
    "04": "Migration Map",   "05": "Canonical Pairs", "06": "Timeframes",
    "07": "Precision & Time","08": "Data Contract",   "09": "Rate Limit",
    "10": "Error",           "11": "Cache",           "12": "Storage",
    "13": "Bootstrap",       "14": "Incremental",     "15": "Supply",
    "16": "OHLCV",           "17": "Exchange Volume", "18": "Exchange Price",
    "19": "Exchange MC",     "20": "Exchange Reliability",
    "21": "Data Reliability","22": "Exchange Dominance",
    "23": "Kitchen Price",   "24": "Kitchen Volume",  "25": "Kitchen MC",
    "26": "Kitchen Coverage","27": "Ranking",         "28": "Grouping",
    "29": "Kitchen Dominance","30": "Snapshot",
}

REQUIRED = [
    "test_name", "item_ref", "description", "key_numbers",
    "executed_at", "script_path", "data",
]


def load_approved():
    """Return list of filenames from approved_tests.tsv."""
    result = []
    if not os.path.exists(APPROVED):
        return result
    for line in open(APPROVED, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if parts and parts[0].strip():
            result.append(parts[0].strip())
    return result


def load_pending():
    """Return list of [item, test, priority, why] rows."""
    result = []
    if not os.path.exists(PENDING):
        return result
    for line in open(PENDING, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        result.append(line.split("\t"))
    return result


def load_and_validate(filename):
    """Load JSON, validate 7 fields, validate script_path exists.
    Returns (dict, error_str_or_None).
    """
    path = os.path.join(EVIDENCE, filename)
    if not os.path.exists(path):
        return None, f"file not found: {path}"

    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except Exception as e:
        return None, f"json parse error: {e}"

    if not isinstance(d, dict):
        return None, "top-level JSON must be an object"

    missing = [k for k in REQUIRED if k not in d]
    if missing:
        return None, f"missing fields: {missing}"

    # Validate script_path exists
    script = d.get("script_path", "")
    if not isinstance(script, str) or not script:
        return None, "script_path must be a non-empty string"
    if not os.path.exists(script):
        return None, f"script_path does not exist: {script}"

    # Normalize item_ref to list
    item_ref = d.get("item_ref")
    if isinstance(item_ref, str):
        item_ref = [item_ref]
    elif not isinstance(item_ref, list):
        return None, "item_ref must be a list or string"
    if not item_ref:
        return None, "item_ref cannot be empty"

    normalized = []
    for item in item_ref:
        s = str(item).strip()
        if len(s) == 1:
            s = s.zfill(2)
        if s not in ITEMS:
            return None, f"invalid item_ref '{item}' (not in 01-30)"
        if s not in normalized:
            normalized.append(s)

    d["item_ref"] = normalized

    # Validate key_numbers is a dict
    if not isinstance(d.get("key_numbers"), dict):
        return None, "key_numbers must be an object"

    # Validate data is a dict
    if not isinstance(d.get("data"), dict):
        return None, "data must be an object"

    return d, None


def fmt_kn(kn):
    """Format key_numbers dict as 'k=v | k=v'."""
    if not isinstance(kn, dict):
        return "-"
    if not kn:
        return "-"
    parts = [f"{k}={v}" for k, v in list(kn.items())[:6]]
    return " | ".join(parts)


def main():
    approved = load_approved()
    pending = load_pending()
    by_item = {num: [] for num in ITEMS}
    errors = []
    valid_count = 0

    for fn in approved:
        d, err = load_and_validate(fn)
        if err:
            errors.append(f"{fn}: {err}")
            continue
        valid_count += 1
        for item in d["item_ref"]:
            by_item[item].append({
                "file": fn,
                "date": str(d.get("executed_at", "-"))[:10],
                "description": str(d.get("description", "-")),
                "key_numbers": fmt_kn(d["key_numbers"]),
            })

    items_covered = sum(1 for v in by_item.values() if v)
    now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    with open(OUT, "w", encoding="utf-8") as out:
        out.write("# MANIFEST.md — Approved Tests Registry (v2)\n\n")
        out.write(f"**Generated:** {now}\n")
        out.write(f"**Approved tests:** {valid_count} | **Errors:** {len(errors)}\n")
        out.write(f"**Items with tests:** {items_covered}/30\n\n")

        out.write("## Workflow\n\n")
        out.write("1. تست جدید → از `TEMPLATE_test.py` کپی → JSON + Script → commit\n")
        out.write("2. Owner تأیید → یک خط به `tests/evidence/approved_tests.tsv`\n")
        out.write("3. `python3 tests/evidence/gen_manifest.py`\n\n")
        out.write("**JSON باید ۷ فیلد داشته باشد:** `test_name`, `item_ref`, `description`, "
                  "`key_numbers`, `executed_at`, `script_path`, `data`\n\n")
        out.write("**Template:** `tests/evidence/TEMPLATE_test.py`\n\n---\n\n")

        out.write("## Item Coverage\n\n")
        out.write("| Item | Name | Tests |\n")
        out.write("|---|---|---|\n")
        for num in sorted(ITEMS.keys()):
            count = len(by_item[num])
            marker = "✅" if count > 0 else "⬜"
            out.write(f"| {num} | {ITEMS[num]} | {marker} {count} |\n")
        out.write("\n---\n\n")

        for num in sorted(ITEMS.keys()):
            tests = by_item[num]
            out.write(f"## Item_{num} — {ITEMS[num]}\n\n")
            if not tests:
                out.write("_هیچ تستی تأیید نشده_\n\n")
                continue
            out.write("| File | Date | Description | Key Numbers |\n")
            out.write("|---|---|---|---|\n")
            for t in sorted(tests, key=lambda x: x["file"]):
                out.write(f"| {t['file']} | {t['date']} | {t['description']} | "
                          f"{t['key_numbers']} |\n")
            out.write("\n")

        out.write("---\n\n## PENDING Tests\n\n")
        if pending:
            out.write("| Item | Test | P | Why |\n")
            out.write("|---|---|---|---|\n")
            for p in pending:
                p = list(p) + [""] * (4 - len(p))
                out.write(f"| {p[0]} | {p[1]} | {p[2]} | {p[3]} |\n")
        else:
            out.write("_هیچ تست PENDING ثبت نشده_\n")

        if errors:
            out.write("\n---\n\n## Errors\n\n")
            for e in errors:
                out.write(f"- `{e}`\n")

    print(f"OK: approved={valid_count} errors={len(errors)} items_covered={items_covered}/30")

    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for e in errors:
            print(f"  ✗ {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
