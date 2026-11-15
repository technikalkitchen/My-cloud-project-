#!/usr/bin/env python3
"""cmc_classify — Classify the 125 Universe assets (stablecoin/regular/wrapped).
Strictly follows TEAM_PROTOCOL §11 and Test 1 naming.
"""
import json
import datetime
import os
import sys

TEST_NAME = "cmc_classify"
ITEM_REF = ["03"]
DESCRIPTION = "Classification of 125 universe assets based on CMC tags"

INPUT_125 = "tests/evidence/cmc_top125_fetch_2026-11-15.json"
INPUT_TAGS = "tests/evidence/cmc_tags_fetch_2026-11-15.json"

def main():
    # Fail fast if inputs missing
    for f in [INPUT_125, INPUT_TAGS]:
        if not os.path.exists(f):
            print(f"ERROR: required input not found: {f}")
            sys.exit(1)

    top125_data = json.load(open(INPUT_125, encoding="utf-8"))
    assets = top125_data["data"]["universe_symbols_list"]

    tags_data = json.load(open(INPUT_TAGS, encoding="utf-8"))
    tags_map = tags_data["data"]["tags_by_symbol"]

    classification = {}
    stablecoins = []
    regular = []
    wrapped = []
    support_assets = []

    for a in assets:
        sym = a["symbol"]
        tags = tags_map.get(sym, {}).get("tags", [])
        
        if "stablecoin" in tags:
            classification[sym] = "stablecoin"
            stablecoins.append(sym)
            if sym == "USDT":
                support_assets.append(sym)
        elif any("wrapped" in t for t in tags):
            classification[sym] = "wrapped"
            wrapped.append(sym)
        else:
            classification[sym] = "regular"
            regular.append(sym)

    if len(stablecoins) == 0:
        print("WARNING: 0 stablecoins — expected ~13. Check tags file.")

    # طبق اصلاح AM-03: همه با _count و هماهنگ با تست ۱
    key_numbers = {
        "total_count": len(assets),
        "stablecoin_count": len(stablecoins),
        "regular_count": len(regular),
        "wrapped_count": len(wrapped),
        "support_count": len(support_assets),
    }

    result = {
        "test_name": TEST_NAME,
        "item_ref": ITEM_REF,
        "description": DESCRIPTION,
        "key_numbers": key_numbers,
        "executed_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "script_path": f"tests/evidence/scripts/{TEST_NAME}.py",
        # طبق اصلاح AM-03: پسوند _symbols_list برای لیست‌ها
        "data": {
            "classification_map": classification,
            "stablecoins_list": sorted(stablecoins),
            "wrapped_symbols_list": sorted(wrapped),
            "support_asset_symbols_list": sorted(support_assets),
        },
    }

    date = datetime.date.today().isoformat()
    path = f"tests/evidence/{TEST_NAME}_{date}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"OK: {path}")
    print(f"    total_count={key_numbers['total_count']}, "
          f"stablecoin_count={key_numbers['stablecoin_count']}, "
          f"regular_count={key_numbers['regular_count']}, "
          f"wrapped_count={key_numbers['wrapped_count']}, "
          f"support_count={key_numbers['support_count']}")

if __name__ == "__main__":
    main()
