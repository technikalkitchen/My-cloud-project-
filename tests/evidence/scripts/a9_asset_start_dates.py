import json
import os
import sys
import urllib.request
import urllib.error
import time
from datetime import datetime, timezone

TOP150_FILE = 'tests/evidence/cmc_top150_2026-11-08.json'
SUPPLY_FILE = 'results/supply_timeseries/supply_timeseries_2026-11-07.json'
OUTPUT_FILE = 'tests/evidence/a9_asset_start_dates_2026-11-08.json'
SUMMARY_FILE = 'tests/evidence/a9_asset_start_dates_2026-11-08_summary.md'

SLEEP = 0.5
TIMEOUT = 15
MAX_RETRIES = 2
COINBASE_YEARS = [2017, 2018, 2019, 2020, 2021, 2022, 2023]

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

def get_binance_oldest(symbol, quote):
    try:
        url = f'https://data-api.binance.vision/api/v3/klines?symbol={symbol}{quote}&interval=1d&startTime=0&limit=1'
        r = json.loads(http_get(url))
        if isinstance(r, list) and r:
            return {'status': 'TESTED', 'date': fmt_date(int(r[0][0]))}
    except Exception:
        pass
    return {'status': 'NOT_FOUND'}

def get_okx_oldest(symbol, quote):
    try:
        url = f'https://www.okx.com/api/v5/market/history-candles?instId={symbol}-{quote}&bar=1D&after=1483228800000&limit=1'
        r = json.loads(http_get(url))
        if r.get('data'):
            return {'status': 'TESTED', 'date': fmt_date(int(r['data'][-1][0]))}
    except Exception:
        pass
    return {'status': 'NOT_FOUND'}

def get_coinbase_oldest(symbol, quote):
    # 1-year windows → MAY be imprecise (66-day offset if >300 candles)
    for year in COINBASE_YEARS:
        try:
            url = f'https://api.exchange.coinbase.com/products/{symbol}-{quote}/candles?granularity=86400&start={year}-01-01T00:00:00Z&end={year}-12-31T23:59:59Z'
            r = json.loads(http_get(url))
            if isinstance(r, list) and r:
                return {'status': 'TESTED', 'date': fmt_date(int(r[-1][0]) * 1000), 'imprecise': True}
        except Exception:
            pass
        time.sleep(SLEEP)
    return {'status': 'NOT_FOUND'}

def get_bitstamp_oldest(symbol, quote):
    try:
        pair = f'{symbol.lower()}{quote.lower()}'
        url = f'https://www.bitstamp.net/api/v2/ohlc/{pair}/?step=86400&limit=1&start=1420070400'
        r = json.loads(http_get(url))
        ohlc = r.get('data', {}).get('ohlc', [])
        if ohlc:
            return {'status': 'TESTED', 'date': fmt_date(int(ohlc[0]['timestamp']) * 1000)}
    except Exception:
        pass
    return {'status': 'NOT_FOUND'}

def get_bybit_oldest(symbol, quote):
    try:
        url = f'https://api.bybit.com/v5/market/kline?category=spot&symbol={symbol}{quote}&interval=D&start=1483228800000&limit=1'
        r = json.loads(http_get(url))
        lst = r.get('result', {}).get('list', [])
        if lst:
            return {'status': 'TESTED', 'date': fmt_date(int(lst[-1][0]))}
    except Exception:
        pass
    return {'status': 'NOT_FOUND'}

def try_both_quotes(fn, symbol):
    r = fn(symbol, 'USDT')
    if r['status'] == 'TESTED':
        return {'quote': 'USDT', **r}
    time.sleep(SLEEP)
    r = fn(symbol, 'USD')
    if r['status'] == 'TESTED':
        return {'quote': 'USD', **r}
    return {'quote': None, 'status': 'NOT_FOUND'}

def main():
    print('=== A9 v2: Asset Start Dates ===')
    print()

    if not os.path.exists(TOP150_FILE):
        print(f'FATAL: {TOP150_FILE} not found (run cmc_top150_fetch.py first)')
        sys.exit(1)
    with open(TOP150_FILE) as f:
        top150 = json.load(f)
    assets = top150['assets']
    print(f'Assets: {len(assets)}')

    supply_start = {}
    if os.path.exists(SUPPLY_FILE):
        with open(SUPPLY_FILE) as f:
            supply = json.load(f)
        for sym, data in supply.items():
            if data and isinstance(data, list):
                dates = [d['date'] for d in data if d.get('date')]
                if dates:
                    supply_start[sym] = min(dates)
        print(f'Supply assets: {len(supply_start)}')
    else:
        print(f'WARNING: {SUPPLY_FILE} not found')

    output = {}
    t0 = time.time()

    for i, a in enumerate(assets, 1):
        sym = a['symbol']
        if i % 10 == 0 or i == 1:
            print(f'[{i}/{len(assets)}] {sym} (elapsed {time.time()-t0:.0f}s)')

        entry = {
            'rank': a['rank'],
            'cmc_id': a['cmc_id'],
            'supply_start': supply_start.get(sym),
            'exchanges': {},
        }

        for ex_name, fn in [
            ('Binance', get_binance_oldest),
            ('OKX', get_okx_oldest),
            ('Coinbase', get_coinbase_oldest),
            ('Bitstamp', get_bitstamp_oldest),
            ('Bybit', get_bybit_oldest),
        ]:
            r = try_both_quotes(fn, sym)
            entry['exchanges'][ex_name] = {
                'quote': r.get('quote'),
                'status': r.get('status'),
                'price_start': r.get('date'),
                'imprecise': r.get('imprecise', False),
            }
            time.sleep(SLEEP)

        for ex_name, ex_data in entry['exchanges'].items():
            ps = ex_data.get('price_start')
            ss = entry['supply_start']
            if ps and ss:
                ex_data['effective_start'] = max(ps, ss)
            else:
                ex_data['effective_start'] = None

        output[sym] = entry

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    total = len(output)
    with_price = sum(1 for e in output.values() if any(x['status'] == 'TESTED' for x in e['exchanges'].values()))
    with_supply = sum(1 for e in output.values() if e['supply_start'])
    with_eff = sum(1 for e in output.values() if any(x.get('effective_start') for x in e['exchanges'].values()))

    lines = ['# A9 Asset Start Dates Summary v2', '', f'**Generated:** {datetime.now(timezone.utc).isoformat()}', '']
    lines.append('## Coverage')
    lines.append(f'- Total assets: {total}')
    lines.append(f'- With price in ≥1 exchange: {with_price}')
    lines.append(f'- With supply: {with_supply}')
    lines.append(f'- With effective_start: {with_eff}')
    lines.append('')
    lines.append('## Per-exchange coverage')
    for ex in ['Binance', 'OKX', 'Coinbase', 'Bitstamp', 'Bybit']:
        cnt = sum(1 for e in output.values() if e['exchanges'].get(ex, {}).get('status') == 'TESTED')
        lines.append(f'- {ex}: {cnt}/{total}')
    lines.append('')
    lines.append('## ⚠️ Coinbase imprecision')
    lines.append('Coinbase uses 1-year windows → if >300 candles in range, only last 300 returned (66-day offset possible).')
    lines.append('For precise Coinbase dates, use 6-month windows (not implemented in v2 — deferred).')
    lines.append('')
    lines.append('## Missing all exchanges')
    missing = [s for s, e in output.items() if all(x['status'] != 'TESTED' for x in e['exchanges'].values())]
    lines.append(f'- {len(missing)}: {", ".join(missing[:30])}')
    lines.append('')
    lines.append('## Assets with no supply')
    no_supply = [s for s, e in output.items() if not e['supply_start']]
    lines.append(f'- {len(no_supply)}: {", ".join(no_supply[:30])}')

    with open(SUMMARY_FILE, 'w') as f:
        f.write('\n'.join(lines))

    print()
    print('=== Summary ===')
    print(f'Total: {total}')
    print(f'With price (≥1): {with_price}')
    print(f'With supply: {with_supply}')
    print(f'With effective_start: {with_eff}')
    print(f'Output: {OUTPUT_FILE}')
    print(f'Summary: {SUMMARY_FILE}')
    print(f'Elapsed: {time.time()-t0:.0f}s')
    print('=== A9 v2 COMPLETE ===')

if __name__ == '__main__':
    main()
