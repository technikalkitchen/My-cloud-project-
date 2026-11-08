import json
import os
import sys
import urllib.request
import urllib.error
import time
from datetime import datetime, timezone

OKX_BASE = 'https://www.okx.com/api/v5/market'
TOP150_FILE = 'tests/evidence/cmc_top150_2026-11-08.json'
OUTPUT_FILE = 'tests/evidence/a9_okx_2026-11-09.json'

SLEEP = 0.5
TIMEOUT = 15
MAX_RETRIES = 2
NOW_MS = int(datetime.now(timezone.utc).timestamp() * 1000)
TS_2017 = 1483228800000
TS_2019 = 1546300800000

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
            return {'status': 'OK', 'count': len(r['data']), 'data': r['data'], 'raw': r}
        return {'status': 'EMPTY', 'count': 0, 'data': [], 'raw': r}
    except Exception as e:
        return {'status': 'ERROR', 'error': str(e)[:100], 'count': 0, 'data': [], 'raw': {}}

def print_raw(raw, max_len=1200):
    s = json.dumps(raw)
    if len(s) > max_len:
        s = s[:max_len] + f'... [truncated {len(s)-max_len} chars]'
    print(f'    raw: {s}')

def run_diagnostic():
    print('=== Section 1: Diagnostic Tests (8) ===')
    results = []

    # [1] after=2017, limit=1 → expect EMPTY
    print('\n[1] history-candles after=2017-01-01, limit=1')
    print('    Expected: EMPTY (BTC-USDT starts 2018 on OKX)')
    r = fetch_okx('history-candles', {'instId': 'BTC-USDT', 'bar': '1D', 'after': TS_2017, 'limit': 1})
    print(f'    status={r["status"]}, count={r["count"]}')
    print_raw(r['raw'])
    ok1 = r['status'] == 'EMPTY'
    print(f'    matches_expected={ok1}')
    results.append(ok1)
    time.sleep(SLEEP)

    # [2] after=2019, limit=1 → expect 1 candle ~2018-12-31
    print('\n[2] history-candles after=2019-01-01, limit=1')
    print('    Expected: OK, count=1, ts~2018-12-31')
    r = fetch_okx('history-candles', {'instId': 'BTC-USDT', 'bar': '1D', 'after': TS_2019, 'limit': 1})
    print(f'    status={r["status"]}, count={r["count"]}')
    if r['data']:
        print(f'    ts={fmt_date(int(r["data"][-1][0]))}')
    print_raw(r['raw'])
    ok2 = r['status'] == 'OK' and r['count'] == 1
    print(f'    matches_expected={ok2}')
    results.append(ok2)
    time.sleep(SLEEP)

    # [3] after=2019, limit=100 → expect 100
    print('\n[3] history-candles after=2019-01-01, limit=100')
    print('    Expected: OK, count=100')
    r = fetch_okx('history-candles', {'instId': 'BTC-USDT', 'bar': '1D', 'after': TS_2019, 'limit': 100})
    print(f'    status={r["status"]}, count={r["count"]}')
    if r['data']:
        print(f'    newest={fmt_date(int(r["data"][0][0]))}, oldest={fmt_date(int(r["data"][-1][0]))}')
    print_raw(r['raw'])
    ok3 = r['status'] == 'OK' and r['count'] == 100
    print(f'    matches_expected={ok3}')
    results.append(ok3)
    time.sleep(SLEEP)

    # [4] before=2017, limit=1 → informational (before=newer records)
    print('\n[4] history-candles before=2017-01-01, limit=1')
    print('    Expected: OK or EMPTY (before=newer records)')
    r = fetch_okx('history-candles', {'instId': 'BTC-USDT', 'bar': '1D', 'before': TS_2017, 'limit': 1})
    print(f'    status={r["status"]}, count={r["count"]}')
    if r['data']:
        print(f'    ts={fmt_date(int(r["data"][-1][0]))}')
    print_raw(r['raw'])
    ok4 = r['status'] in ('OK', 'EMPTY')
    print(f'    matches_expected={ok4}')
    results.append(ok4)
    time.sleep(SLEEP)

    # [5] candles (not history) → informational
    print('\n[5] candles (not history) after=2019-01-01, limit=1')
    print('    Expected: OK or EMPTY (candles = recent only)')
    r = fetch_okx('candles', {'instId': 'BTC-USDT', 'bar': '1D', 'after': TS_2019, 'limit': 1})
    print(f'    status={r["status"]}, count={r["count"]}')
    if r['data']:
        print(f'    ts={fmt_date(int(r["data"][-1][0]))}')
    print_raw(r['raw'])
    print('    (informational)')
    results.append(True)
    time.sleep(SLEEP)

    # [6] after=0 → informational
    print('\n[6] history-candles after=0, limit=1')
    print('    Expected: EMPTY or OK')
    r = fetch_okx('history-candles', {'instId': 'BTC-USDT', 'bar': '1D', 'after': 0, 'limit': 1})
    print(f'    status={r["status"]}, count={r["count"]}')
    print_raw(r['raw'])
    print('    (informational)')
    results.append(True)
    time.sleep(SLEEP)

    # [7] pagination verification (CRITICAL)
    print('\n[7] pagination test: after=2019, then after=oldest_found')
    print('    Expected: second call returns older candles')
    r1 = fetch_okx('history-candles', {'instId': 'BTC-USDT', 'bar': '1D', 'after': TS_2019, 'limit': 100})
    if r1['data']:
        oldest1 = int(r1['data'][-1][0])
        print(f'    batch1 oldest={fmt_date(oldest1)}')
        time.sleep(SLEEP)
        r2 = fetch_okx('history-candles', {'instId': 'BTC-USDT', 'bar': '1D', 'after': oldest1, 'limit': 100})
        if r2['data']:
            oldest2 = int(r2['data'][-1][0])
            print(f'    batch2 oldest={fmt_date(oldest2)}')
            ok7 = oldest2 < oldest1
            print(f'    pagination_works={ok7} (expected: oldest2 < oldest1)')
        else:
            ok7 = False
            print(f'    batch2 status={r2["status"]} (no pagination possible)')
    else:
        ok7 = False
        print(f'    batch1 status={r1["status"]} (pagination test failed)')
    results.append(ok7)
    time.sleep(SLEEP)

    # [8] limit=300 cap verification (NEW)
    print('\n[8] history-candles after=2019-01-01, limit=300')
    print('    Expected: OK, count=300 (A3 confirmed OKX cap)')
    r = fetch_okx('history-candles', {'instId': 'BTC-USDT', 'bar': '1D', 'after': TS_2019, 'limit': 300})
    print(f'    status={r["status"]}, count={r["count"]}')
    if r['data']:
        print(f'    newest={fmt_date(int(r["data"][0][0]))}, oldest={fmt_date(int(r["data"][-1][0]))}')
    print_raw(r['raw'])
    ok8 = r['status'] == 'OK' and r['count'] == 300
    print(f'    matches_expected={ok8}')
    results.append(ok8)

    passed = sum(results)
    print(f'\n=== Diagnostic: {passed}/8 passed ===')
    return all(results)

def walk_back_oldest(symbol, quote='USDT'):
    instId = f'{symbol}-{quote}'
    current_after = NOW_MS
    oldest_found = None

    for iteration in range(20):
        r = fetch_okx('history-candles', {'instId': instId, 'bar': '1D', 'after': current_after, 'limit': 300})
        if r['status'] != 'OK' or not r['data']:
            break
        oldest_in_batch = int(r['data'][-1][0])
        oldest_found = oldest_in_batch
        if len(r['data']) < 300:
            break
        current_after = oldest_in_batch
        time.sleep(SLEEP)

    return oldest_found

def find_oldest(symbol):
    ts = walk_back_oldest(symbol, 'USDT')
    if ts:
        return {'status': 'TESTED', 'quote': 'USDT', 'price_start': fmt_date(ts), 'ts_ms': ts}
    time.sleep(SLEEP)
    ts = walk_back_oldest(symbol, 'USD')
    if ts:
        return {'status': 'TESTED', 'quote': 'USD', 'price_start': fmt_date(ts), 'ts_ms': ts}
    return {'status': 'NOT_LISTED', 'quote': None, 'price_start': None, 'ts_ms': None}

def main():
    if not run_diagnostic():
        print('\nFATAL: Diagnostic failed. Stop per R-16.')
        print('Report raw output to AM before proceeding.')
        sys.exit(1)

    print('\n=== Section 2: Full OKX scan (150 assets) ===')
    if not os.path.exists(TOP150_FILE):
        print(f'FATAL: {TOP150_FILE} not found')
        sys.exit(1)

    with open(TOP150_FILE) as f:
        top150 = json.load(f)
    assets = top150['assets']
    print(f'Assets: {len(assets)}')

    existing = {}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE) as f:
            existing = json.load(f)
        print(f'Resume: {len(existing)} already done')

    t0 = time.time()
    for i, a in enumerate(assets, 1):
        sym = a['symbol']
        if sym in existing:
            continue
        if i % 10 == 0 or i == 1:
            print(f'[{i}/{len(assets)}] {sym} (elapsed {time.time()-t0:.0f}s)')

        result = find_oldest(sym)
        existing[sym] = {
            'rank': a['rank'],
            'cmc_id': a['cmc_id'],
            'okx': result,
        }

        if i % 10 == 0:
            os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(existing, f, indent=2, default=str)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(existing, f, indent=2, default=str)

    tested = sum(1 for e in existing.values() if e['okx']['status'] == 'TESTED')
    print(f'\n=== Summary ===')
    print(f'Total: {len(existing)}')
    print(f'Tested: {tested}')
    print(f'NOT_LISTED: {len(existing) - tested}')
    print(f'Output: {OUTPUT_FILE}')
    print(f'Elapsed: {time.time()-t0:.0f}s')
    print('=== A9 OKX COMPLETE ===')

if __name__ == '__main__':
    main()
