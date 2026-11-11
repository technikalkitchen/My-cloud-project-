import json
import urllib.request
import time

IDS = {"SPX": 28081, "XPL": 36645, "FF": 38482, "PIEVERSE": 38849, "KITE": 38828, "MON": 30495, "NFT": 9816}

print("=== Checking Live Supply for 7 NO_DATA ===")
for sym, cid in IDS.items():
    url = f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/historical?id={cid}&convertId=2781&timeStart=1483228800&timeEnd=1483315200&interval=1d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://coinmarketcap.com/"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            quotes = data.get("data", {}).get("quotes", [])
            status = "HAS DATA" if quotes else "NO DATA"
            print(f"{sym} (ID {cid}): {status}")
    except Exception as e:
        print(f"{sym} (ID {cid}): ERROR ({str(e)[:30]})")
    time.sleep(0.5)
print("=== Done ===")
