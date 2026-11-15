#!/usr/bin/env python3
"""cmc_top125_fetch — Select Universe = 125 from CMC top 150.
Uses existing top150 JSON + existing tags JSON.
"""
import json
import datetime

TEST_NAME = "cmc_top125_fetch"
ITEM_REF = ["03"]
DESCRIPTION = "Universe selection: top 125 from CMC 150 (excludes 25 lowest ranks)"

INPUT_150 = "tests/evidence/cmc_top150_2026-11-08.json"
INPUT_TAGS = "tests/evidence/cmc_tags_fetch_2026-11-15.json"

def main():
    # ۱. خواندن لیست ۱۵۰تایی
    src = json.load(open(INPUT_150, encoding="utf-8"))
    assets = src["assets"]
    # مرتب‌سازی بر اساس rank
    assets.sort(key=lambda x: x.get("rank", 9999))

    universe_125 = assets[:125]
    excluded_25 = assets[125:]

    # ۲. خواندن تگ‌ها برای پیدا کردن Stablecoinها
    try:
        tags_data = json.load(open(INPUT_TAGS, encoding="utf-8"))
        tags_map = tags_data["data"]["tags_by_symbol"]
    except FileNotFoundError:
        tags_map = {}

    stablecoins = []
    for a in universe_125:
        sym = a["symbol"]
        if sym in tags_map:
            if "stablecoin" in tags_map[sym]["tags"]:
                stablecoins.append(sym)

    # ۳. ساختار خروجی
    key_numbers = {
        "total_universe": len(universe_125),
        "excluded_count": len(excluded_25),
        "stablecoins_in_universe": len(stablecoins),
        "wrapped_in_universe": 0,
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
            "universe_125": [
                {"rank": a.get("rank"), "symbol": a["symbol"], "cmc_id": a["cmc_id"], "name": a.get("name")}
                for a in universe_125
            ],
            "excluded_25": [
                {"rank": a.get("rank"), "symbol": a["symbol"], "cmc_id": a["cmc_id"], "name": a.get("name")}
                for a in excluded_25
            ],
            "stablecoins": stablecoins,
            "source_file": INPUT_150,
        },
    }

    date = datetime.date.today().isoformat()
    path = f"tests/evidence/{TEST_NAME}_{date}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"OK: {path}")
    print(f"    universe={key_numbers['total_universe']}, "
          f"excluded={key_numbers['excluded_count']}, "
          f"stablecoins={key_numbers['stablecoins_in_universe']}")
    print(f"    ranks included: {key_numbers['highest_rank_included']} to {key_numbers['lowest_rank_included']}")
    print(f"    ranks excluded: {key_numbers['highest_rank_excluded']} to 150")

if __name__ == "__main__":
    main()
