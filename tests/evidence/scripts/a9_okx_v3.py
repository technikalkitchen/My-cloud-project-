import json
import os
import sys
import urllib.request
import urllib.error
import time
from datetime import datetime, timezone

OKX_BASE = 'https://www.okx.com/api/v5/market'
TOP150_FILE = 'tests/evidence/cmc_top150_2026-11-08.json'
V1_FILE = 'tests/evidence/a9_okx_2026-11-09.json'
OUTPUT_FILE = 'tests/evidence/a9_okx_v3_2026-11-09.json'

SLEEP = 0.5
TIMEOUT = 15
MAX_RETRIES = 2
MAX_ITER = 20
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


def walk_back_quote(symbol, quote, max_iter=MAX_ITER, limit=300):
    instId = f'{symbol}-{quote}'
    current_after = NOW_MS
    oldest_found = None
    iterations = 0
    imprecise = False
    for iteration in range(max_iter):
        r = fetch_okx('history-candles', {'instId': instId, 'bar': '1D', 'after': current_after, 'limit': limit})
        iterations += 1
        if r['status'] != 'OK' or not r['data']:
            break
        oldest_in_batch = int(r['data'][-1][0])
        oldest_found = oldest_in_batch
        if len(r['data']) < limit:
            break
        current_after = oldest_in_batch
        if iteration == max_iter - 1:
            imprecise = True
        time.sleep(SLEEP)
    if oldest_found:
        return {
            'status': 'TESTED',
            'oldest': fmt_date(oldest_found),
            'oldest_ms': oldest_found,
            'iterations': iterations,
            'imprecise': imprecise,
        }
    return {'status': 'NOT_LISTED', 'iterations': iterations}


def run_diagnostic():
    print('=== Phase 1: Diagnostic ===')
    critical_pass = []

    # [1] BTC-BTC (critical)
    print('\n[1] BTC-BTC (CRITICAL: self pair)')
    r = fetch_okx('history-candles', {'instId': 'BTC-BTC', 'bar': '1D', 'limit': 1})
    ok1 = r['status'] != 'OK'
    print(f'    status={r["status"]}, count={r["count"]} | matches_expected={ok1}')
    critical_pass.append(ok1)
    time.sleep(SLEEP)

    # [2] BTC-USDT (critical)
    print('\n[2] BTC-USDT (CRITICAL: baseline)')
    r2 = walk_back_quote('BTC', 'USDT', max_iter=15)
    date2 = r2.get('oldest') if r2.get('status') == 'TESTED' else None
    ok2 = date2 is not None and date2.startswith('2017-')
    print(f'    oldest={date2} | matches_expected(2017-*)={ok2}')
    critical_pass.append(ok2)

    # [3] BTC-USD (informational)
    print('\n[3] BTC-USD (informational)')
    r3 = walk_back_quote('BTC', 'USD', max_iter=15)
    date3 = r3.get('oldest') if r3.get('status') == 'TESTED' else None
    print(f'    oldest={date3 if date3 else "NOT_LISTED"}')

    # [4-7] BTC-quote for older assets (INFORMATIONAL)
    btc_tests = []
    for sym in ['ZEC', 'DASH', 'SEI', 'TAO']:
        print(f'\n[{len(btc_tests)+4}] {sym}-BTC (informational)')
        r_btc = walk_back_quote(sym, 'BTC', max_iter=15)
        d = r_btc.get('oldest') if r_btc.get('status') == 'TESTED' else None
        ok = d is not None
        print(f'    oldest={d} | TESTED={ok}')
        btc_tests.append(ok)
        time.sleep(SLEEP)

    print(f'\n=== Diagnostic Summary ===')
    print(f'Critical (BTC-BTC, BTC-USDT): {"PASS" if all(critical_pass) else "FAIL"}')
    print(f'BTC-quote tests (informational): {sum(btc_tests)}/4 passed')

    if not all(critical_pass):
        print('FATAL: Critical diagnostic failed. Per R-16: STOP.')
        return False
    if not any(btc_tests):
        print('WARNING: All 4 BTC-quote tests failed. BTC-quote may not work on OKX.')
        print('         Continuing anyway (BTC-quote is informational in this diagnostic).')
    return True


def scan_asset(symbol, v1_data):
    result = {}

    v1_entry = v1_data.get(symbol, {}).get('okx', {})
    usdt_status = v1_entry.get('status', 'NOT_LISTED')
    result['USDT'] = {
        'status': usdt_status,
        'oldest': v1_entry.get('price_start'),
        'oldest_ms': v1_entry.get('ts_ms'),
        'source': 'v1',
        'imprecise': None if usdt_status == 'TESTED' else False,
    }

    btc = walk_back_quote(symbol, 'BTC')
    result['BTC'] = btc
    time.sleep(SLEEP)

    usd = walk_back_quote(symbol, 'USD')
    result['USD'] = usd

    dates = []
    for q in ['USDT', 'BTC', 'USD']:
        if result[q].get('status') == 'TESTED' and result[q].get('oldest'):
            dates.append(result[q]['oldest'])
    result['effective_min'] = min(dates) if dates else None
    result['imprecise'] = any(
        result[q].get('imprecise') for q in ['BTC', 'USD']
        if result[q].get('status') == 'TESTED'
    )
    return result


def main():
    print('=== A9 OKX v3.2: USDT(v1) + BTC + USD ===')
    print()

    if not run_diagnostic():
        sys.exit(1)

    print('\n=== Phase 2: Full scan (150 assets × BTC + USD) ===')
    if not os.path.exists(TOP150_FILE):
        print(f'FATAL: {TOP150_FILE} not found')
        sys.exit(1)
    if not os.path.exists(V1_FILE):
        print(f'FATAL: {V1_FILE} not found')
        sys.exit(1)

    with open(TOP150_FILE) as f:
        top150 = json.load(f)
    with open(V1_FILE) as f:
        v1_data = json.load(f)
    assets = top150['assets']
    print(f'Assets: {len(assets)}')

    existing = {}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE) as f:
            saved = json.load(f)
            existing = saved.get('assets', {})
        print(f'Resume: {len(existing)} done')

    summary = {
        'improved_via_btc': [],
        'improved_via_usd': [],
        'still_not_listed': [],
        'newly_discovered': [],
    }
    t0 = time.time()

    for i, a in enumerate(assets, 1):
        sym = a['symbol']
        if sym in existing:
            continue
        if i % 10 == 0 or i == 1:
            print(f'[{i}/{len(assets)}] {sym} (elapsed {time.time()-t0:.0f}s)')

        result = scan_asset(sym, v1_data)
        existing[sym] = result

        usdt_s = result['USDT'].get('status')
        btc_s = result['BTC'].get('status')
        usd_s = result['USD'].get('status')
        usdt_d = result['USDT'].get('oldest')
        btc_d = result['BTC'].get('oldest')
        usd_d = result['USD'].get('oldest')

        if btc_d and (not usdt_d or btc_d < usdt_d):
            summary['improved_via_btc'].append(sym)
        if usd_d and (not usdt_d or usd_d < usdt_d):
            summary['improved_via_usd'].append(sym)

        if usdt_s == 'NOT_LISTED' and (btc_s == 'TESTED' or usd_s == 'TESTED'):
            summary['newly_discovered'].append(sym)

        if usdt_s == 'NOT_LISTED' and btc_s == 'NOT_LISTED' and usd_s == 'NOT_LISTED':
            summary['still_not_listed'].append(sym)

        if i % 10 == 0:
            os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
            with open(OUTPUT_FILE, 'w') as f:
                json.dump({
                    'generated_at': datetime.now(timezone.utc).isoformat(),
                    'assets': existing,
                    'summary': summary,
                }, f, default=str)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump({
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'source_v1': V1_FILE,
            'assets': existing,
            'summary': summary,
        }, f, indent=2, default=str)

    print()
    print('=== Summary ===')
    print(f'Total: {len(existing)}')
    print(f'Improved via BTC: {len(summary["improved_via_btc"])}')
    print(f'Improved via USD: {len(summary["improved_via_usd"])}')
    print(f'Newly discovered: {len(summary["newly_discovered"])}')
    print(f'Still NOT_LISTED: {len(summary["still_not_listed"])}')
    print(f'Output: {OUTPUT_FILE}')
    print(f'Elapsed: {time.time()-t0:.0f}s')
    print('=== A9 OKX v3.2 COMPLETE ===')


if __name__ == '__main__':
    main()
