import json
import os
import sys
import urllib.request
import urllib.error
import time
from datetime import datetime, timezone

OKX_BASE = 'https://www.okx.com/api/v5/market'
OUTPUT_FILE = 'tests/evidence/A6_A7_okx_correction_2026-11-09.json'

SLEEP = 0.5
TIMEOUT = 15
MAX_RETRIES = 2
MAX_ITER = 20
NOW_MS = int(datetime.now(timezone.utc).timestamp() * 1000)

TARGET_ASSETS = ['MATIC', 'POL', 'RNDR', 'RENDER', 'FTM', 'S']
QUOTES = ['USDT', 'USD', 'USDC']

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

def walk_back_oldest(symbol, quote):
    instId = f'{symbol}-{quote}'
    current_after = NOW_MS
    oldest_found = None
    iterations = 0
    imprecise = False

    for iteration in range(MAX_ITER):
        r = fetch_okx('history-candles', {'instId': instId, 'bar': '1D', 'after': current_after, 'limit': 300})
        iterations += 1
        if r['status'] != 'OK' or not r['data']:
            break
        oldest_in_batch = int(r['data'][-1][0])
        oldest_found = oldest_in_batch
        if len(r['data']) < 300:
            break
        current_after = oldest_in_batch
        if iteration == MAX_ITER - 1:
            imprecise = True
        time.sleep(SLEEP)

    if oldest_found:
        return {
            'status': 'TESTED',
            'quote': quote,
            'oldest': fmt_date(oldest_found),
            'oldest_ms': oldest_found,
            'iterations': iterations,
            'imprecise': imprecise,
        }
    return {'status': 'NOT_LISTED', 'quote': quote, 'iterations': iterations}

def test_asset(symbol):
    print(f'  {symbol}:')
    result = {'quotes_tested': []}
    for quote in QUOTES:
        r = walk_back_oldest(symbol, quote)
        result[quote] = r
        result['quotes_tested'].append(quote)
        if r['status'] == 'TESTED':
            print(f'    {quote}: TESTED | {r["oldest"]} | iter={r["iterations"]} | imprecise={r["imprecise"]}')
            result['best'] = {'quote': quote, 'oldest': r['oldest'], 'oldest_ms': r['oldest_ms']}
            return result
        else:
            print(f'    {quote}: NOT_LISTED (iter={r["iterations"]})')
        time.sleep(SLEEP)
    result['best'] = None
    return result

def main():
    print('=== A6_A7 OKX Correction (walk-back) ===')
    print()

    t0 = time.time()
    corrections = {}
    summary = {'tested': [], 'not_listed': [], 'imprecise': []}

    for sym in TARGET_ASSETS:
        r = test_asset(sym)
        corrections[sym] = r
        if r['best']:
            summary['tested'].append({'symbol': sym, 'quote': r['best']['quote'], 'oldest': r['best']['oldest']})
            if r[r['best']['quote']].get('imprecise'):
                summary['imprecise'].append(sym)
        else:
            summary['not_listed'].append(sym)

        # R-27 incremental save
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w') as f:
            json.dump({
                'corrected_at': datetime.now(timezone.utc).isoformat(),
                'reason': 'OKX walk-back correction for A6_A7 bug (after=2017 returned empty)',
                'source_discovery_file': 'tests/evidence/A6_A7_discovery_2026-11-08.json (unchanged)',
                'assets': corrections,
            }, f, indent=2, default=str)
        print()

    print('=== Summary ===')
    print(f'Tested: {len(summary["tested"])}')
    for t in summary['tested']:
        print(f'  {t["symbol"]} ({t["quote"]}): {t["oldest"]}')
    print(f'NOT_LISTED: {len(summary["not_listed"])}')
    if summary['not_listed']:
        print(f'  {summary["not_listed"]}')
    if summary['imprecise']:
        print(f'Imprecise (Stage B): {summary["imprecise"]}')
    print(f'Output: {OUTPUT_FILE}')
    print(f'Elapsed: {time.time()-t0:.0f}s')
    print('=== COMPLETE ===')

if __name__ == '__main__':
    main()
