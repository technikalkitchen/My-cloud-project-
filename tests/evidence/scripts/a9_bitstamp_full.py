import json
import os
import sys
import urllib.request
import urllib.error
import time
from datetime import datetime, timezone, timedelta

BASE_URL = 'https://www.bitstamp.net/api/v2/ohlc/{pair}/'
TOP150_FILE = 'tests/evidence/cmc_top150_2026-11-08.json'
OUTPUT_FILE = 'tests/evidence/a9_bitstamp_2026-11-11.json'

TIMEOUT = 15
MAX_RETRIES = 2
SLEEP = 1.0
MAX_ITER = 10
QUOTES = ['usdt', 'usd', 'btc']

def http_get(url, max_retries=MAX_RETRIES):
    for attempt in range(max_retries + 1):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {'__http_error__': 404}
            if e.code in (429, 502, 503) and attempt < max_retries:
                time.sleep(3.0 ** attempt)
                continue
            return {'__http_error__': e.code}
        except Exception as e:
            if attempt < max_retries:
                time.sleep(3.0 ** attempt)
                continue
            return {'__error__': str(e)[:100]}

def query_window(pair, start_ts, end_ts):
    # Bitstamp uses unix timestamps for start/end
    url = f'{BASE_URL.format(pair=pair)}?step=86400&limit=1000&start={start_ts}&end={end_ts}'
    raw = http_get(url)
    if isinstance(raw, dict):
        if raw.get('__http_error__') == 404:
            return {'status': 'NOT_LISTED'}
        return {'status': 'ERROR', 'detail': str(raw)[:100]}
    try:
        r = json.loads(raw)
        ohlc = r.get('data', {}).get('ohlc', [])
        return {'status': 'OK', 'count': len(ohlc), 'data': ohlc}
    except Exception as e:
        return {'status': 'JSON_ERROR', 'error': str(e)[:100]}

def find_oldest(pair, max_iter=MAX_ITER):
    now = datetime.now(timezone.utc)
    end_ts = int(now.timestamp())
    last_oldest = None
    last_count = None
    iterations = 0

    for i in range(max_iter):
        # 1000 days back
        start_ts = end_ts - (1000 * 86400)
        r = query_window(pair, start_ts, end_ts)
        iterations += 1
        time.sleep(SLEEP)

        if r['status'] == 'NOT_LISTED':
            if last_oldest is None:
                return {'status': 'NOT_LISTED', 'iterations': iterations}
            return {'status': 'TESTED', 'oldest': last_oldest, 'iterations': iterations, 'imprecise': last_count == 1000}
        if r['status'] != 'OK':
            return {'status': 'ERROR', 'detail': str(r)[:100], 'iterations': iterations}

        if r['count'] == 0:
            if last_oldest is None:
                return {'status': 'NOT_LISTED', 'iterations': iterations}
            return {'status': 'TESTED', 'oldest': last_oldest, 'iterations': iterations, 'imprecise': last_count == 1000}

        # Bitstamp returns newest first, so min timestamp is the last element
        oldest_in_window = int(r['data'][-1]['timestamp']) * 1000
        last_oldest = oldest_in_window
        last_count = r['count']

        if r['count'] < 1000:
            return {'status': 'TESTED', 'oldest': last_oldest, 'iterations': iterations, 'imprecise': False}

        end_ts = start_ts

    if last_oldest:
        return {'status': 'TESTED', 'oldest': last_oldest, 'iterations': iterations, 'imprecise': True, 'max_iter_reached': True}
    return {'status': 'NOT_LISTED', 'iterations': iterations}

def fmt(ts_ms):
    if not ts_ms:
        return None
    return datetime.fromtimestamp(int(ts_ms) / 1000, tz=timezone.utc).strftime('%Y-%m-%d')

def main():
    print('=== A9 Bitstamp Full Scan ===')
    print(f'Time: {datetime.now(timezone.utc).isoformat()}')
    
    if not os.path.exists(TOP150_FILE):
        print(f'FATAL: {TOP150_FILE} not found')
        return 1

    with open(TOP150_FILE) as f:
        top150 = json.load(f)
    assets = top150['assets']
    print(f'Assets: {len(assets)}')

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
            pair = f'{sym.lower()}{quote}'
            r = find_oldest(pair)
            if r['status'] == 'TESTED':
                entry['quotes'][quote] = {
                    'status': 'TESTED',
                    'oldest': fmt(r['oldest']),
                    'oldest_ms': r['oldest'],
                    'iterations': r.get('iterations'),
                    'imprecise': r.get('imprecise', False),
                }
                break
            entry['quotes'][quote] = {
                'status': r['status'],
                'iterations': r.get('iterations'),
            }

        # Compute effective_min
        candidates = [entry['quotes'][q]['oldest_ms'] for q in QUOTES if entry['quotes'].get(q, {}).get('status') == 'TESTED']
        entry['effective_min'] = fmt(min(candidates)) if candidates else None
        entry['imprecise'] = any(entry['quotes'][q].get('imprecise') for q in QUOTES if entry['quotes'].get(q, {}).get('status') == 'TESTED')

        existing[sym] = entry

        if i % 10 == 0:
            os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
            with open(OUTPUT_FILE, 'w') as f:
                json.dump({'generated_at': datetime.now(timezone.utc).isoformat(), 'assets': existing}, f, default=str)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump({'generated_at': datetime.now(timezone.utc).isoformat(), 'assets': existing}, f, indent=2, default=str)

    with_effective = sum(1 for e in existing.values() if e.get('effective_min'))
    not_listed = sum(1 for e in existing.values() if not e.get('effective_min'))
    
    print('\n=== Summary ===')
    print(f'Total assets: {len(existing)}')
    print(f'With effective_min: {with_effective}')
    print(f'NOT_LISTED: {not_listed}')
    print(f'Elapsed: {time.time()-t0:.0f}s')
    print('=== COMPLETE ===')
    return 0

if __name__ == '__main__':
    sys.exit(main())
