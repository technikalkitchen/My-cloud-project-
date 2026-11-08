import json
import os
import sys
import urllib.request
import urllib.error
import time
from datetime import datetime, timezone

OKX_BASE = 'https://www.okx.com/api/v5/market'
OKX_FILE = 'tests/evidence/a9_okx_2026-11-09.json'
OUTPUT_FILE = 'tests/evidence/a9_okx_usdc_retry_2026-11-09.json'

SLEEP = 0.5
TIMEOUT = 15
MAX_RETRIES = 2
MAX_ITER = 2
NOW_MS = int(datetime.now(timezone.utc).timestamp() * 1000)

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

def fmt_date(ms):
    if not ms:
        return None
    return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).strftime('%Y-%m-%d')

def fetch_okx(endpoint, params):
    qs = '&'.join(f'{k}={v}' for k, v in params.items())
    url = f'{OKX_BASE}/{endpoint}?{qs}'
    try:
        r = json.loads(http_get(url))
        if r.get('code') == '0' and r.get('data'):
            return {'status': 'OK', 'count': len(r['data']), 'data': r['data']}
        return {'status': 'EMPTY', 'count': 0, 'data': []}
    except Exception as e:
        return {'status': 'ERROR', 'error': str(e)[:100], 'count': 0, 'data': []}

def walk_back_usdc(symbol, max_iter=MAX_ITER):
    instId = f'{symbol}-USDC'
    current_after = NOW_MS
    oldest_found = None
    iterations = 0
    imprecise = False

    for iteration in range(max_iter):
        r = fetch_okx('history-candles', {'instId': instId, 'bar': '1D', 'after': current_after, 'limit': 300})
        iterations += 1
        if r['status'] != 'OK' or not r['data']:
            break
        oldest_in_batch = int(r['data'][-1][0])
        oldest_found = oldest_in_batch
        if len(r['data']) < 300:
            break
        current_after = oldest_in_batch
        if iteration == max_iter - 1:
            imprecise = True
        time.sleep(SLEEP)

    return oldest_found, iterations, imprecise

def main():
    print('=== OKX USDC Retry ===')

    if not os.path.exists(OKX_FILE):
        print(f'FATAL: {OKX_FILE} not found')
        sys.exit(1)

    with open(OKX_FILE) as f:
        data = json.load(f)

    not_listed = [sym for sym, v in data.items() if v.get('okx', {}).get('status') == 'NOT_LISTED']
    print(f'NOT_LISTED assets: {len(not_listed)}')
    print()

    output = {}
    found_with_usdc = []
    still_not_listed = []

    t0 = time.time()
    for i, sym in enumerate(not_listed, 1):
        print(f'[{i}/{len(not_listed)}] {sym}')
        ts, iterations, imprecise = walk_back_usdc(sym, MAX_ITER)

        if ts:
            entry = {
                'status': 'TESTED',
                'quote': 'USDC',
                'price_start': fmt_date(ts),
                'iterations': iterations,
                'imprecise': imprecise,
            }
            found_with_usdc.append(sym)
            print(f'  TESTED | {fmt_date(ts)} | iter={iterations} | imprecise={imprecise}')
        else:
            entry = {
                'status': 'NOT_LISTED',
                'quote': 'USDC',
                'iterations': iterations,
            }
            still_not_listed.append(sym)
            print(f'  NOT_LISTED (after {iterations} iter)')

        output[sym] = entry
        time.sleep(SLEEP)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print()
    print('=== Summary ===')
    print(f'Total: {len(not_listed)}')
    print(f'Found with USDC: {len(found_with_usdc)}')
    if found_with_usdc:
        print(f'  {found_with_usdc}')
    print(f'Still NOT_LISTED: {len(still_not_listed)}')
    print(f'Output: {OUTPUT_FILE}')
    print(f'Elapsed: {time.time()-t0:.0f}s')
    print('=== COMPLETE ===')

if __name__ == '__main__':
    main()
