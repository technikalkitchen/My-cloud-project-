#!/usr/bin/env python3
"""cmc_tags_fetch — Fetch CMC tags via Keyless API (batch=50).
Endpoint: https://pro-api.coinmarketcap.com/public-api/v2/cryptocurrency/info
"""
import json
import time
import urllib.request
import urllib.error
import datetime

TEST_NAME = "cmc_tags_fetch"
ITEM_REF = ["03"]
DESCRIPTION = "Tags for 150 CMC assets — wrapped/stablecoin classification source"

INPUT = "tests/evidence/cmc_top150_2026-11-08.json"
BASE_URL = "https://pro-api.coinmarketcap.com/public-api/v2/cryptocurrency/info"
UA = "Mozilla/5.0"
BATCH_SIZE = 50


def http_get(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Accept": "application/json",
            })
            raw = urllib.request.urlopen(req, timeout=30).read()
            return json.loads(raw)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            return None
        except Exception:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            return None
    return None


def fetch_batch(ids):
    url = f"{BASE_URL}?id={','.join(str(i) for i in ids)}&aux=tags"
    resp = http_get(url)
    if not isinstance(resp, dict):
        return None
    status = resp.get("status", {})
    if isinstance(status, dict):
        ec = status.get("error_code")
        if ec not in (None, 0, "0"):
            return None
    return resp.get("data")


def main():
    src = json.load(open(INPUT, encoding="utf-8"))
    assets = src["assets"]
    asset_ids = [a["cmc_id"] for a in assets]
    print(f"Total: {len(asset_ids)} ids, batch_size={BATCH_SIZE}")

    all_data = {}
    for i in range(0, len(asset_ids), BATCH_SIZE):
        chunk = asset_ids[i:i + BATCH_SIZE]
        print(f"  batch {i+1}-{i+len(chunk)}/{len(asset_ids)}")
        data = fetch_batch(chunk)
        if data:
            all_data.update(data)
        time.sleep(2.0)

    print(f"Fetched: {len(all_data)}/{len(asset_ids)}")

    tags_map = {}
    missing = []
    for a in assets:
        cid = str(a["cmc_id"])
        if cid not in all_data:
            missing.append({"cmc_id": a["cmc_id"], "symbol": a["symbol"]})
            continue
        entry = all_data[cid]
        tags = entry.get("tags", []) or []
        tags_map[a["symbol"]] = {
            "cmc_id": a["cmc_id"],
            "name": entry.get("name"),
            "slug": entry.get("slug"),
            "tags": tags,
        }

    wrapped = sorted(s for s, v in tags_map.items() if "wrapped" in v["tags"])
    stablecoin = sorted(s for s, v in tags_map.items() if "stablecoin" in v["tags"])

    key_numbers = {
        "fetched": len(tags_map),
        "missing": len(missing),
        "wrapped_tagged": len(wrapped),
        "stablecoin_tagged": len(stablecoin),
        "remaining_after_wrapped": len(assets) - len(wrapped),
    }

    result = {
        "test_name": TEST_NAME,
        "item_ref": ITEM_REF,
        "description": DESCRIPTION,
        "key_numbers": key_numbers,
        "executed_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "script_path": f"tests/evidence/scripts/{TEST_NAME}.py",
        "data": {
            "tags_by_symbol": tags_map,
            "missing": missing,
            "wrapped": wrapped,
            "stablecoin": stablecoin,
        },
    }
    date = datetime.date.today().isoformat()
    path = f"tests/evidence/{TEST_NAME}_{date}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"OK: {path}")
    print(f"    fetched={len(tags_map)}/{len(asset_ids)}, "
          f"wrapped={len(wrapped)}, stablecoin={len(stablecoin)}, "
          f"remaining={len(assets) - len(wrapped)}, missing={len(missing)}")


if __name__ == "__main__":
    main()
