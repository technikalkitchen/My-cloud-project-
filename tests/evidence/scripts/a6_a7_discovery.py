import json
import os
import sys
import urllib.request
import urllib.error
import time
from datetime import datetime, timezone, timedelta

CMC_LISTING_URL = 'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing'
SLEEP = 0.5
TIMEOUT = 60
MAX_RETRIES = 2

SUPPLY_FILE = 'results/final_supply_harvest/run_40351779336/final-125-supply-results/final_125_supply.json'
OUTPUT_FILE = 'tests/evidence/A6_A7_discovery_2026-11-08.json'
SUMMARY_FILE = 'tests/evidence/A6_A7_discovery_2026-11-08_summary.md'

KNOWN_MIGRATIONS = [
    {'from_symbol': 'FTM', 'to_symbol': 'S', 'from_cmc_id': 3375, 'to_cmc_id': 32684, 'type': 'migration_new_id'},
    {'from_symbol': 'MATIC', 'to_symbol': 'POL', 'from_cmc_id': 28321, 'to_cmc_id': 28321, 'type': 'rename'},
    {'from_symbol': 'RNDR', 'to_symbol': 'RENDER', 'from_cmc_id': 5690, 'to_cmc_id': 5690, 'type': 'rename'},
]

KNOWN_DELISTED = ['FTT', 'LUNA', 'UST']
KNOWN_SURVIVORS = ['LUNC']

def http_get(url, timeout=TIMEOUT, max_retries=MAX_RETRIES):
    for attempt in range(max_retries + 1):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            return urllib.request.urlopen(req, timeout=timeout).read()
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

def fetch_cmc_listing():
    print('Fetching CMC top 1000 (2 pages)...')
    coins = []
    for start in [1, 501]:
        url = f'{CMC_LISTING_URL}?start={start}&limit=500&sortBy=market_cap&sortType=desc&convert=USD&cryptoType=all&tagType=all&audited=false'
        try:
            data = json.loads(http_get(url))
            page = data.get('data', {}).get('cryptoCurrencyList', [])
            coins.extend(page)
            print(f'  Page start={start}: {len(page)} coins')
        except Exception as e:
            print(f'  Page start={start}: ERROR {type(e).__name__}: {e}')
        time.sleep(SLEEP)
    return coins

def oldest_candle(exchange, base, quote):
    try:
        if exchange == 'Binance':
            url = f'https://data-api.binance.vision/api/v3/klines?symbol={base}{quote}&interval=1d&startTime=1483228800000&limit=1'
            r = json.loads(http_get(url))
            if isinstance(r, list) and r:
                return {'status': 'TESTED', 'oldest': int(r[0][0])}
        elif exchange == 'OKX':
            url = f'https://www.okx.com/api/v5/market/history-candles?instId={base}-{quote}&bar=1D&after=1483228800000&limit=1'
            r = json.loads(http_get(url))
            if r.get('data'):
                return {'status': 'TESTED', 'oldest': int(r['data'][-1][0])}
        elif exchange == 'Coinbase':
            for year in [2017, 2018, 2019, 2020, 2021, 2022]:
                try:
                    url = f'https://api.exchange.coinbase.com/products/{base}-{quote}/candles?granularity=86400&start={year}-01-01T00:00:00Z&end={year}-12-31T23:59:59Z'
                    r = json.loads(http_get(url))
                    if isinstance(r, list) and r:
                        return {'status': 'TESTED', 'oldest': int(r[-1][0]) * 1000, 'found_year': year}
                except Exception:
                    pass
                time.sleep(SLEEP)
        elif exchange == 'Bitstamp':
            pair = f'{base.lower()}{quote.lower()}'
            url = f'https://www.bitstamp.net/api/v2/ohlc/{pair}/?step=86400&limit=1&start=1483228800'
            r = json.loads(http_get(url))
            ohlc = r.get('data', {}).get('ohlc', [])
            if ohlc:
                return {'status': 'TESTED', 'oldest': int(ohlc[0]['timestamp']) * 1000}
        elif exchange == 'Bybit':
            url = f'https://api.bybit.com/v5/market/kline?category=spot&symbol={base}{quote}&interval=D&start=1483228800000&limit=1'
            r = json.loads(http_get(url))
            lst = r.get('result', {}).get('list', [])
            if lst:
                return {'status': 'TESTED', 'oldest': int(lst[-1][0])}
        return {'status': 'NOT_LISTED'}
    except Exception as e:
        return {'status': 'ERROR', 'error': f'{type(e).__name__}: {str(e)[:80]}'}

def newest_candle(exchange, base, quote):
    try:
        if exchange == 'Binance':
            url = f'https://data-api.binance.vision/api/v3/klines?symbol={base}{quote}&interval=1d&limit=1'
            r = json.loads(http_get(url))
            if isinstance(r, list) and r:
                return {'status': 'TESTED', 'newest': int(r[-1][0])}
        elif exchange == 'OKX':
            url = f'https://www.okx.com/api/v5/market/history-candles?instId={base}-{quote}&bar=1D&limit=1'
            r = json.loads(http_get(url))
            if r.get('data'):
                return {'status': 'TESTED', 'newest': int(r['data'][0][0])}
        elif exchange == 'Coinbase':
            end = datetime.now(timezone.utc)
            start = end - timedelta(days=2)
            url = f'https://api.exchange.coinbase.com/products/{base}-{quote}/candles?granularity=86400&start={start.isoformat()}&end={end.isoformat()}'
            r = json.loads(http_get(url))
            if isinstance(r, list) and r:
                return {'status': 'TESTED', 'newest': int(r[0][0]) * 1000}
        elif exchange == 'Bitstamp':
            pair = f'{base.lower()}{quote.lower()}'
            url = f'https://www.bitstamp.net/api/v2/ohlc/{pair}/?step=86400&limit=1'
            r = json.loads(http_get(url))
            ohlc = r.get('data', {}).get('ohlc', [])
            if ohlc:
                return {'status': 'TESTED', 'newest': int(ohlc[0]['timestamp']) * 1000}
        elif exchange == 'Bybit':
            url = f'https://api.bybit.com/v5/market/kline?category=spot&symbol={base}{quote}&interval=D&limit=1'
            r = json.loads(http_get(url))
            lst = r.get('result', {}).get('list', [])
            if lst:
                return {'status': 'TESTED', 'newest': int(lst[0][0])}
        return {'status': 'NOT_LISTED'}
    except Exception as e:
        return {'status': 'ERROR', 'error': f'{type(e).__name__}: {str(e)[:80]}'}

def test_asset_on_exchanges(symbol):
    print(f'  Testing {symbol}...')
    result = {}
    for ex in ['Binance', 'OKX', 'Coinbase', 'Bitstamp', 'Bybit']:
        first_usdt = oldest_candle(ex, symbol, 'USDT')
        time.sleep(SLEEP)
        if first_usdt.get('status') == 'TESTED':
            last = newest_candle(ex, symbol, 'USDT')
            time.sleep(SLEEP)
            result[ex] = {'status': 'TESTED', 'quote': 'USDT', 'oldest': first_usdt.get('oldest'), 'newest': last.get('newest')}
        else:
            first_usd = oldest_candle(ex, symbol, 'USD')
            time.sleep(SLEEP)
            if first_usd.get('status') == 'TESTED':
                last = newest_candle(ex, symbol, 'USD')
                time.sleep(SLEEP)
                result[ex] = {'status': 'TESTED', 'quote': 'USD', 'oldest': first_usd.get('oldest'), 'newest': last.get('newest')}
            else:
                result[ex] = first_usdt
    return result

def detect_from_supply(supply, cmc_by_id, cmc_by_symbol):
    migrations = []
    delisted_candidates = []
    cmc_id_changes = []
    for entry in supply:
        if entry.get('status') != 'FILLED':
            continue
        sym = entry['symbol']
        old_id = entry.get('cmc_id')
        if not old_id:
            continue
        if old_id in cmc_by_id:
            current = cmc_by_id[old_id]
            if current['symbol'] != sym:
                # Fix 1: skip case-only rename (XAUT -> XAUt)
                if sym.lower() == current['symbol'].lower():
                    continue
                migrations.append({'from_symbol': sym, 'to_symbol': current['symbol'], 'from_cmc_id': old_id, 'to_cmc_id': old_id, 'type': 'rename'})
        else:
            same_sym = cmc_by_symbol.get(sym, [])
            other_ids = [c for c in same_sym if c['id'] != old_id]
            if other_ids:
                alt = other_ids[0]
                # Fix 2+3: same symbol, id changed (KMNO) → cmc_id_changes
                if alt['symbol'] == sym:
                    cmc_id_changes.append({
                        'symbol': sym,
                        'old_cmc_id': old_id,
                        'new_cmc_id': alt['id'],
                        'reason': 'cmc_id_changed_same_symbol',
                    })
                    continue
                migrations.append({'from_symbol': sym, 'to_symbol': alt['symbol'], 'from_cmc_id': old_id, 'to_cmc_id': alt['id'], 'type': 'migration_new_id'})
            else:
                delisted_candidates.append({'symbol': sym, 'cmc_id': old_id, 'reason': 'not_in_top_1000_no_alt_id'})
    return migrations, delisted_candidates, cmc_id_changes

def fmt_ts(ms):
    if not ms:
        return None
    return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).strftime('%Y-%m-%d')

def main():
    print('=== A6+A7 Discovery v4 (clean) ===')
    print()

    if not os.path.exists(SUPPLY_FILE):
        print(f'FATAL: {SUPPLY_FILE} not found')
        sys.exit(1)
    with open(SUPPLY_FILE) as f:
        supply = json.load(f)
    print(f'Loaded supply: {len(supply)}')

    cmc_coins = fetch_cmc_listing()
    cmc_by_id = {c['id']: c for c in cmc_coins}
    cmc_by_symbol = {}
    for c in cmc_coins:
        cmc_by_symbol.setdefault(c['symbol'], []).append(c)
    print(f'CMC loaded: {len(cmc_coins)}')

    print()
    print('=== Migration Detection ===')
    detected, delisted_candidates, cmc_id_changes = detect_from_supply(supply, cmc_by_id, cmc_by_symbol)
    print(f'Detected migrations: {len(detected)}')
    for m in detected:
        print(f'  {m["from_symbol"]} -> {m["to_symbol"]} [{m["type"]}]')
    print(f'CMC ID changes (separate): {len(cmc_id_changes)}')
    for c in cmc_id_changes:
        print(f'  {c["symbol"]}: {c["old_cmc_id"]} -> {c["new_cmc_id"]}')

    known_froms = {m['from_symbol'] for m in detected}
    added = [m for m in KNOWN_MIGRATIONS if m['from_symbol'] not in known_froms]
    migrations = list(detected) + added
    print(f'Added from KNOWN: {len(added)}')
    print(f'Total migrations: {len(migrations)}')

    known_delisted = [{'symbol': s, 'cmc_id': None, 'reason': 'known_delisted'} for s in KNOWN_DELISTED]
    known_survivors = [{'symbol': s, 'cmc_id': None, 'reason': 'known_survivor'} for s in KNOWN_SURVIVORS]

    print()
    print('=== Exchange Tests ===')
    final = {'migrations': [], 'delisted': [], 'survivors': [], 'cmc_id_changes': cmc_id_changes}

    for m in migrations:
        print(f'\nMigration: {m["from_symbol"]} -> {m["to_symbol"]}')
        e = dict(m)
        e['from_data'] = test_asset_on_exchanges(m['from_symbol'])
        e['to_data'] = test_asset_on_exchanges(m['to_symbol'])
        final['migrations'].append(e)

    seen = {d['symbol'] for d in known_delisted + known_survivors}
    for d in delisted_candidates:
        if d['symbol'] not in seen:
            known_delisted.append(d)
            seen.add(d['symbol'])

    for d in known_delisted:
        print(f'\nDelisted: {d["symbol"]}')
        e = dict(d)
        e['data'] = test_asset_on_exchanges(d['symbol'])
        final['delisted'].append(e)

    for s in known_survivors:
        print(f'\nSurvivor: {s["symbol"]}')
        e = dict(s)
        e['data'] = test_asset_on_exchanges(s['symbol'])
        final['survivors'].append(e)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(final, f, separators=(',', ':'), default=str)

    lines = ['# A6+A7 Discovery Summary v4', '', f'**Generated:** {datetime.now(timezone.utc).isoformat()}', '']
    lines.append(f'## Migrations ({len(final["migrations"])})')
    for m in final['migrations']:
        lines.append(f'- **{m["from_symbol"]} → {m["to_symbol"]}** ({m["type"]})')
        for ex, d in m['from_data'].items():
            lines.append(f'  - {ex} (from): {d.get("status")} {fmt_ts(d.get("oldest")) or ""} → {fmt_ts(d.get("newest")) or ""}')
    lines.append('')
    lines.append(f'## Delisted ({len(final["delisted"])})')
    for d in final['delisted']:
        lines.append(f'- **{d["symbol"]}** ({d["reason"]})')
        for ex, dd in d['data'].items():
            lines.append(f'  - {ex}: {dd.get("status")} {fmt_ts(dd.get("oldest")) or ""} → {fmt_ts(dd.get("newest")) or ""}')
    lines.append('')
    lines.append(f'## Survivors ({len(final["survivors"])})')
    for s in final['survivors']:
        lines.append(f'- **{s["symbol"]}**')
        for ex, dd in s['data'].items():
            lines.append(f'  - {ex}: {dd.get("status")} {fmt_ts(dd.get("oldest")) or ""} → {fmt_ts(dd.get("newest")) or ""}')
    lines.append('')
    lines.append(f'## CMC ID Changes ({len(final["cmc_id_changes"])}) — symbol unchanged, CMC ID changed')
    for c in final['cmc_id_changes']:
        lines.append(f'- **{c["symbol"]}**: {c["old_cmc_id"]} → {c["new_cmc_id"]}')
    lines.append('')
    lines.append(f'## Files\n- JSON: `{OUTPUT_FILE}`\n- Summary: `{SUMMARY_FILE}`')

    with open(SUMMARY_FILE, 'w') as f:
        f.write('\n'.join(lines))

    size_kb = os.path.getsize(OUTPUT_FILE) / 1024
    print()
    print('=== Summary ===')
    print(f'Migrations: {len(final["migrations"])}')
    print(f'Delisted: {len(final["delisted"])}')
    print(f'Survivors: {len(final["survivors"])}')
    print(f'CMC ID Changes: {len(final["cmc_id_changes"])}')
    print(f'Output: {OUTPUT_FILE} ({size_kb:.1f} KB)')
    print()
    print('=== A6+A7 v4 COMPLETE ===')

if __name__ == '__main__':
    main()
