import json
import os
import sys
import urllib.request
import urllib.error
import time
from datetime import datetime, timezone, timedelta

COINBASE_BASE = 'https://api.exchange.coinbase.com'
TOP150_FILE = 'tests/evidence/cmc_top150_2026-11-08.json'
OUTPUT_FILE = 'tests/evidence/a9_coinbase_2026-11-11.json'

TIMEOUT = 15
MAX_RETRIES = 2
SLEEP = 0.5
MAX_ITER = 25
QUOTES = ['USDT', 'USD']  # USDC skip per Owner decision (11 Nov)

def http_get(url, max_retries=MAX_RETRIES):
    for attempt in range(max_retries + 1):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            return urllib.request.urlopen(req, timeout=TIMEOUT).read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {'__http_error__': 404}
            if e.code in (429, 502, 503) and attempt < max_retries:
                time.sleep(2.0 ** attempt)
                continue
            return {'__http_error__': e.code}
        except Exception as e:
            if attempt < max_retries:
                time.sleep(2.0 ** attempt)
                continue
            return {'__error__': str(e)[:100]}

def query_window(product, start_dt, end_dt):
    start_iso = start_dt.strftime('%Y-%m-%dT00:00:00Z')
    end_iso = end_dt.strftime('%Y-%m-%dT23:59:59Z')
    url = f'{COINBASE_BASE}/products/{product}/candles?granularity=86400&start={start_iso}&end={end_iso}'
    raw = http_get(url)
    if isinstance(raw, dict):
        if raw.get('__http_error__') == 404:
            return {'status': 'NOT_LISTED'}
        return {'status': 'ERROR', 'detail': str(raw)[:100]}
    try:
        r = json.loads(raw)
        if isinstance(r, list):
            return {'status': 'OK', 'count': len(r), 'data': r}
        return {'status': 'UNEXPECTED', 'raw': str(r)[:100]}
    except Exception as e:
        return {'status': 'JSON_ERROR', 'error': str(e)[:100]}

def fmt(ts_ms):
    if not ts_ms:
        return None
    return datetime.fromtimestamp(int(ts_ms) / 1000, tz=timezone.utc).strftime('%Y-%m-%d')

def find_oldest(product, max_iter=MAX_ITER):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    end = today
    last_oldest = None
    last_count = None
    iterations = 0

    for i in range(max_iter):
        start = end - timedelta(days=182)
        r = query_window(product, start, end)
        iterations += 1
        time.sleep(SLEEP)

        if r['status'] == 'NOT_LISTED':
            if last_oldest is None:
                return {'status': 'NOT_LISTED', 'iterations': iterations}
            return {'status': 'TESTED', 'oldest': last_oldest, 'count_at_start': last_count,
                    'iterations': iterations, 'imprecise': last_count >= 182}
        if r['status'] != 'OK':
            return {'status': 'ERROR', 'detail': str(r)[:100], 'iterations': iterations}

        if r['count'] == 0:
            if last_oldest is None:
                return {'status': 'NOT_LISTED', 'iterations': iterations}
            return {'status': 'TESTED', 'oldest': last_oldest, 'count_at_start': last_count,
                    'iterations': iterations, 'imprecise': last_count >= 182}

        oldest_in_window = min(int(c[0]) for c in r['data']) * 1000
        last_oldest = oldest_in_window
        last_count = r['count']

        if r['count'] < 182:
            return {'status': 'TESTED', 'oldest': last_oldest, 'count_at_start': last_count,
                    'iterations': iterations, 'imprecise': False}

        end = start

    if last_oldest:
        return {'status': 'TESTED', 'oldest': last_oldest, 'count_at_start': last_count,
                'iterations': iterations, 'imprecise': True, 'max_iter_reached': True}
    return {'status': 'NOT_LISTED', 'iterations': iterations}

def main():
    print('=== A9 Coinbase Full Scan (150 assets, USDT+USD, 6-month windows) ===')
    print(f'Time: {datetime.now(timezone.utc).isoformat()}')
    print()

    if not os.path.exists(TOP150_FILE):
        print(f'FATAL: {TOP150_FILE} not found')
        return 1

    with open(TOP150_FILE) as f:
        top150 = json.load(f)
    assets = top150['assets']
    print(f'Assets: {len(assets)}')

    # Step 1: USDT-USD start (once, for Converted USD path)
    print('\n=== Step 1: USDT-USD start ===')
    usdt_usd = find_oldest('USDT-USD')
    if usdt_usd['status'] == 'TESTED':
        print(f'USDT-USD: {fmt(usdt_usd["oldest"])} (iter={usdt_usd["iterations"]})')
    else:
        print(f'USDT-USD: {usdt_usd["status"]}')

    # Step 2: Full scan
    print('\n=== Step 2: Full scan (150 assets × USDT + USD) ===')
    existing = {}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE) as f:
            saved = json.load(f)
            existing = saved.get('assets', {})
        print(f'Resume: {len(existing)} done')

    t0 = time.time()
    for i, a in enumerate(assets, 1):
        sym = a['symbol']
        if sym in existing:
            continue
        if i % 10 == 0 or i == 1:
            print(f'[{i}/{len(assets)}] {sym} (elapsed {time.time()-t0:.0f}s)')

        entry = {'rank': a['rank'], 'cmc_id': a['cmc_id'], 'quotes': {}}

        for quote in QUOTES:
            product = f'{sym}-{quote}'
            r = find_oldest(product)
            if r['status'] == 'TESTED':
                entry['quotes'][quote] = {
                    'status': 'TESTED',
                    'oldest': fmt(r['oldest']),
                    'oldest_ms': r['oldest'],
                    'count_at_start': r.get('count_at_start'),
                    'iterations': r.get('iterations'),
                    'imprecise': r.get('imprecise', False),
                }
                break
            entry['quotes'][quote] = {
                'status': r['status'],
                'iterations': r.get('iterations'),
            }

        # Compute effective_min
        usdt_entry = entry['quotes'].get('USDT', {})
        usd_entry = entry['quotes'].get('USD', {})

        direct_start = usdt_entry.get('oldest') if usdt_entry.get('status') == 'TESTED' else None

        converted_start = None
        if usd_entry.get('status') == 'TESTED' and usdt_usd['status'] == 'TESTED':
            usd_ms = usd_entry.get('oldest_ms')
            usdt_usd_ms = usdt_usd.get('oldest')
            if usd_ms and usdt_usd_ms:
                converted_ms = max(usd_ms, usdt_usd_ms)
                converted_start = fmt(converted_ms)

        candidates = [d for d in [direct_start, converted_start] if d]
        entry['effective_min'] = min(candidates) if candidates else None
        entry['direct_start'] = direct_start
        entry['converted_start'] = converted_start
        entry['imprecise'] = bool(usdt_entry.get('imprecise') or (
            converted_start and usd_entry.get('imprecise')
        ))

        existing[sym] = entry

        if i % 10 == 0:
            os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
            with open(OUTPUT_FILE, 'w') as f:
                json.dump({
                    'generated_at': datetime.now(timezone.utc).isoformat(),
                    'usdt_usd_start': fmt(usdt_usd.get('oldest')),
                    'assets': existing,
                }, f, default=str)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump({
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'usdt_usd_start': fmt(usdt_usd.get('oldest')),
            'assets': existing,
        }, f, indent=2, default=str)

    total = len(existing)
    with_effective = sum(1 for e in existing.values() if e.get('effective_min'))
    with_direct = sum(1 for e in existing.values() if e.get('direct_start'))
    with_converted = sum(1 for e in existing.values() if e.get('converted_start'))
    imprecise = sum(1 for e in existing.values() if e.get('imprecise'))
    not_listed = sum(1 for e in existing.values() if not e.get('effective_min'))

    print()
    print('=== Summary ===')
    print(f'Total assets: {total}')
    print(f'With effective_min: {with_effective}')
    print(f'  via Direct USDT: {with_direct}')
    print(f'  via Converted USD: {with_converted}')
    print(f'Imprecise: {imprecise}')
    print(f'NOT_LISTED (no effective): {not_listed}')
    print(f'USDT-USD start: {fmt(usdt_usd.get("oldest"))}')
    print(f'Output: {OUTPUT_FILE}')
    print(f'Elapsed: {time.time()-t0:.0f}s')
    print('=== A9 Coinbase Full COMPLETE ===')
    return 0

if __name__ == '__main__':
    sys.exit(main())
