import json
import os
import urllib.request
import urllib.error
import time
from datetime import datetime, timezone

CMC_URL = 'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing'
OUTPUT_FILE = 'tests/evidence/cmc_top150_2026-11-08.json'
TIMEOUT = 30
MAX_RETRIES = 2

def http_get(url, max_retries=MAX_RETRIES):
    for attempt in range(max_retries + 1):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            return urllib.request.urlopen(req, timeout=TIMEOUT).read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503) and attempt < max_retries:
                time.sleep(2.0 ** attempt)
                continue
            raise
        except Exception:
            if attempt < max_retries:
                time.sleep(2.0 ** attempt)
                continue
            raise

def main():
    print('=== CMC Top 150 Fetch ===')
    url = f'{CMC_URL}?start=1&limit=200&sortBy=market_cap&sortType=desc&convert=USD&cryptoType=all&tagType=all&audited=false'
    try:
        raw = http_get(url)
        data = json.loads(raw)
    except Exception as e:
        print(f'FATAL: {type(e).__name__}: {e}')
        return

    coins = data.get('data', {}).get('cryptoCurrencyList', [])
    print(f'Fetched: {len(coins)} coins')

    top150 = []
    for c in coins:
        top150.append({
            'symbol': c.get('symbol'),
            'cmc_id': c.get('id'),
            'rank': c.get('cmcRank'),
            'market_cap': c.get('quotes', [{}])[0].get('marketCap') if c.get('quotes') else None,
            'name': c.get('name'),
        })
        if len(top150) >= 150:
            break

    output = {
        'fetched_at': datetime.now(timezone.utc).isoformat(),
        'count': len(top150),
        'assets': top150,
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f'Top 150 saved: {OUTPUT_FILE}')
    print(f'  First: {top150[0]["symbol"]} (rank {top150[0]["rank"]})')
    print(f'  Last:  {top150[-1]["symbol"]} (rank {top150[-1]["rank"]})')
    print('=== COMPLETE ===')

if __name__ == '__main__':
    main()
