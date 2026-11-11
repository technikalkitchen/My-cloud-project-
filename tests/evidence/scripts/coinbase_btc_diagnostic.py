import json
import urllib.request
import urllib.error
import time
import sys
from datetime import datetime, timezone

COINBASE_BASE = 'https://api.exchange.coinbase.com'
TIMEOUT = 15
MAX_RETRIES = 2
SLEEP = 0.5

def http_get(url, max_retries=MAX_RETRIES):
    for attempt in range(max_retries + 1):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            return urllib.request.urlopen(req, timeout=TIMEOUT).read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503) and attempt < max_retries:
                time.sleep(2.0 ** attempt)
                continue
            return {'__http_error__': e.code}
        except Exception as e:
            if attempt < max_retries:
                time.sleep(2.0 ** attempt)
                continue
            return {'__error__': str(e)[:100]}

def fetch_candles(product, start_iso, end_iso, granularity=86400):
    url = f'{COINBASE_BASE}/products/{product}/candles?granularity={granularity}&start={start_iso}&end={end_iso}'
    raw = http_get(url)
    if isinstance(raw, dict):
        return raw
    try:
        r = json.loads(raw)
        if isinstance(r, list):
            return {'status': 'OK', 'count': len(r), 'data': r}
        return {'status': 'UNEXPECTED', 'raw': str(r)[:200]}
    except Exception as e:
        return {'status': 'JSON_ERROR', 'error': str(e)[:100]}

def fmt(ts):
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime('%Y-%m-%d')

def run_test(label, product, start_iso, end_iso, granularity=86400):
    print(f'\n[{label}]')
    print(f'  product={product}, range={start_iso} → {end_iso}, granularity={granularity}s')
    r = fetch_candles(product, start_iso, end_iso, granularity)
    if r.get('status') == 'OK':
        print(f'  OK | count={r["count"]}')
        if r['count'] > 0:
            print(f'    first={fmt(r["data"][-1][0])}, last={fmt(r["data"][0][0])}')
        time.sleep(SLEEP)
        return {'result': 'OK', 'count': r['count']}
    if '__http_error__' in r:
        print(f'  HTTP {r["__http_error__"]}')
        time.sleep(SLEEP)
        return {'result': 'HTTP_ERROR', 'code': r['__http_error__']}
    print(f'  ERROR: {r}')
    time.sleep(SLEEP)
    return {'result': 'ERROR', 'detail': str(r)[:200]}

def main():
    print('=== Coinbase BTC Diagnostic (9 tests) ===')
    print(f'Time: {datetime.now(timezone.utc).isoformat()}')
    results = {}

    # ===== TD tests (t1-t7) =====
    results['t1_pre_boundary'] = run_test(
        '1. BTC-USD pre-2015-07 (expect EMPTY)',
        'BTC-USD', '2015-06-01T00:00:00Z', '2015-06-30T23:59:59Z')

    results['t2_post_boundary'] = run_test(
        '2. BTC-USD post-2015-07 (expect OK)',
        'BTC-USD', '2015-08-01T00:00:00Z', '2015-08-31T23:59:59Z')

    results['t3_2020'] = run_test(
        '3. BTC-USD 2020-06 (expect OK)',
        'BTC-USD', '2020-06-01T00:00:00Z', '2020-06-30T23:59:59Z')

    results['t4_usdt'] = run_test(
        '4. BTC-USDT 2020-06 (pair exists?)',
        'BTC-USDT', '2020-06-01T00:00:00Z', '2020-06-30T23:59:59Z')

    results['t5_usdc'] = run_test(
        '5. BTC-USDC 2024-06 (pair exists?)',
        'BTC-USDC', '2024-06-01T00:00:00Z', '2024-06-30T23:59:59Z')

    results['t6_1year'] = run_test(
        '6. 1-year window (candle cap test — expect HTTP 400 if cap=300)',
        'BTC-USD', '2020-01-01T00:00:00Z', '2020-12-31T23:59:59Z')

    results['t7_6month'] = run_test(
        '7. 6-month window (pagination — expect OK)',
        'BTC-USD', '2020-01-01T00:00:00Z', '2020-06-30T23:59:59Z')

    # ===== AM-02 tests (t8-t9) =====
    results['t8_usdt_usd'] = run_test(
        '8. USDT-USD (same-exchange rate, Item_05 §3.6)',
        'USDT-USD', '2020-06-01T00:00:00Z', '2020-06-30T23:59:59Z')

    results['t9_usdc_usd'] = run_test(
        '9. USDC-USD (implied stablecoin, Item_05 §3.4)',
        'USDC-USD', '2020-06-01T00:00:00Z', '2020-06-30T23:59:59Z')

    # ===== Summary =====
    print('\n=== Summary ===')
    for k in ['t1_pre_boundary', 't2_post_boundary', 't3_2020',
              't4_usdt', 't5_usdc', 't6_1year', 't7_6month',
              't8_usdt_usd', 't9_usdc_usd']:
        print(f'{k}: {results[k]}')

    # ===== Interpretation for Item_05 =====
    print('\n=== Item_05 Interpretation ===')
    if results['t4_usdt']['result'] == 'OK':
        print('  BTC-USDT: EXISTS → Direct path (Item_05 §1.1)')
    elif results['t4_usdt'].get('code') == 404:
        print('  BTC-USDT: 404 → NOT DIRECT')
        if results['t8_usdt_usd']['result'] == 'OK':
            print('    BUT USDT-USD exists → Converted via same-exchange rate (§3.3 + §3.6)')
        elif results['t8_usdt_usd'].get('code') == 404:
            print('    USDT-USD also 404 → must use Binance for rate (§3.6 fallback)')
    else:
        print(f'  BTC-USDT: {results["t4_usdt"]}')

    if results['t9_usdc_usd']['result'] == 'OK':
        print('  USDC-USD: EXISTS → Implied stablecoin valid (§3.4)')
    else:
        print(f'  USDC-USD: {results["t9_usdc_usd"]} → check fallback')

    # ===== Readiness =====
    print('\n=== Readiness ===')
    critical_ok = (
        results['t2_post_boundary']['result'] == 'OK' and
        results['t3_2020']['result'] == 'OK'
    )
    pagination_ok = results['t7_6month']['result'] == 'OK'
    cap_confirmed = results['t6_1year'].get('code') == 400 or (
        results['t6_1year']['result'] == 'OK' and results['t6_1year'].get('count', 0) <= 300
    )

    print(f'Critical (t2+t3): {"PASS" if critical_ok else "FAIL"}')
    print(f'6-month pagination (t7): {"PASS" if pagination_ok else "FAIL"}')
    print(f'Candle cap (t6): {"CONFIRMED ≤300" if cap_confirmed else "CHECK — cap might be higher"}')

    if not critical_ok:
        print('\nFATAL: critical tests failed. Cannot proceed with full scan.')
        return 1
    if not pagination_ok:
        print('\nFATAL: 6-month window failed. Pagination approach invalid.')
        return 1

    print('\nREADY for full Coinbase scan with 6-month windows.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
