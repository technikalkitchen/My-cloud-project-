#!/usr/bin/env python3
"""TEMPLATE — Test script with required 7-field JSON output.

HOW TO USE:
    1. Copy this file to tests/evidence/scripts/{TEST_NAME}.py
    2. Edit TEST_NAME, ITEM_REF, DESCRIPTION
    3. Fill in run_test() with your logic
    4. Run: python3 tests/evidence/scripts/{TEST_NAME}.py
    5. Add filename to tests/evidence/approved_tests.tsv (Owner)
    6. Run: python3 tests/evidence/gen_manifest.py
"""
import sys
import json
import datetime

# ═══ EDIT THESE THREE ═══
TEST_NAME = "example_test"           # slug, e.g., "binance_coverage"
ITEM_REF = ["01"]                     # list of item numbers, e.g., ["01", "03"]
DESCRIPTION = "Edit this description"


def run_test():
    """Return (data, key_numbers) — both must be dicts."""
    data = {"sample_key": "sample_value"}
    key_numbers = {"total": 100, "tested": 95}
    return data, key_numbers


def main():
    if TEST_NAME == "example_test":
        sys.exit("ERROR: Edit TEST_NAME, ITEM_REF, DESCRIPTION before running")
    if not ITEM_REF:
        sys.exit("ERROR: ITEM_REF cannot be empty")

    data, key_numbers = run_test()

    if not isinstance(data, dict):
        sys.exit("ERROR: run_test() data must be dict")
    if not isinstance(key_numbers, dict):
        sys.exit("ERROR: run_test() key_numbers must be dict")

    result = {
        "test_name": TEST_NAME,
        "item_ref": ITEM_REF,
        "description": DESCRIPTION,
        "key_numbers": key_numbers,
        "executed_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "script_path": f"tests/evidence/scripts/{TEST_NAME}.py",
        "data": data,
    }

    date = datetime.date.today().isoformat()
    path = f"tests/evidence/{TEST_NAME}_{date}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"OK: {path}")
    print(f"     items: {ITEM_REF}")
    print(f"     key_numbers: {key_numbers}")


if __name__ == "__main__":
    main()
