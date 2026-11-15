#!/usr/bin/env python3
"""cmc_top125_fetch — Select Universe = 125 from CMC top 150.
Strictly selection only. Classification is owned by Test 2.
"""
import json
import datetime
import os
import sys

TEST_NAME = "cmc_top125_fetch"
ITEM_REF = ["03"]
DESCRIPTION = "Universe selection: top 125 from CMC 150 (excludes 25 lowest ranks)"

INPUT_150 = "tests/evidence/cmc_top150_2026-11-08.json"

def main():
    if not os.path.exists(INPUT_150):
        print(f"ERROR: required input not found: {INPUT_150}")
        sys.exit(1)

    src = json.load(open(INPUT_150, encoding="utf-8"))
    assets = src["assets"]
    assets.sort(key=lambda x: x.get("rank", 9999))
    
    universe_125 = assets[:125]
    excluded_25 = assets[125:]

    # فقط و فقط اطلاعات مربوط به انتخاب (بدون هیچ classification)
    key_numbers = {
        "universe_count": len(universe_125),
        "excluded_count": len(excluded_25),
        "highest_rank_included": universe_125[0].get("rank"),
        "lowest_rank_included": universe_125[-1].get("rank"),
        "highest_rank_excluded": excluded_25[0].get("rank") if excluded_25 else None,
    }

    result = {
        "test_name": TEST_NAME,
        "item_ref": ITEM_REF,
        "description": DESCRIPTION,
        "key_numbers": key_numbers,
        "executed_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "script_path": f"tests/evidence/scripts/{TEST_NAME}.py",
        "data": {
            "universe_symbols_list": [
                {"rank": a.get("rank"), "symbol": a["symbol"], "cmc_id": a["cmc_id"], "name": a.get("name")}
                for a in universe_125
            ],
            "excluded_symbols_list": [
                {"rank": a.get("rank"), "symbol": a["symbol"], "cmc_id": a["cmc_id"], "name": a.get("name")}
                for a in excluded_25
            ],
            "source_file": INPUT_150,
        },
    }

    date = datetime.date.today().isoformat()
    path = f"tests/evidence/{TEST_NAME}_{date}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"OK: {path}")
    print(f"    universe_count={key_numbers['universe_count']}, "
          f"excluded_count={key_numbers['excluded_count']}")

if __name__ == "__main__":
    main()
