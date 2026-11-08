import json
import os
import urllib.request
import time
from datetime import datetime, timezone

BYBIT_URL = 'https://api.bybit.com/v5/market'
SLEEP = 0.3
TIMEOUT = 15
TEST_TS = 1698192000000  # 2023-10-25 00:00 UTC

OUTPUT_FILE = 'tests/evidence/pol_bybit_test_2026-11-08.json'

def fetch(url, timeout=TIMEOUT):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        return json.load(urllib.request.urlopen(req, timeout=timeout))
    except Exception as e:
        return {'__error__': f'{type(e).__name__}: {str(e)[:100]}'}

def fmt(ms):
    if not ms:
        return None
    return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M')

print('=== POL on Bybit Test ===')
print(f'Reference date: {fmt(TEST_TS)}')
print()

result = {}

# 1. Instruments info
print('--- 1. POLUSDT instruments info ---')
r = fetch(f'{BYBIT_URL}/instruments-info?category=spot&symbol=POLUSDT')
info = {}
if isinstance(r, dict) and 'result' in r and r['result'].get('list'):
    item = r['result']['list'][0]
    info = {
        'launchTime': item.get('launchTime'),
        'launchTime_fmt': fmt(item.get('launchTime')),
        'status': item.get('status'),
        'baseCoin': item.get('baseCoin'),
        'quoteCoin': item.get('quoteCoin'),
    }
    print(f'  launchTime: {info["launchTime_fmt"]} ({info["launchTime"]})')
    print(f'  status: {info["status"]}')
elif '__error__' in r:
    print(f'  ERROR: {r["__error__"]}')
result['instruments_info'] = info
time.sleep(SLEEP)

# 2. POL price at TEST_TS
print()
print(f'--- 2. POLUSDT price at {fmt(TEST_TS)} ---')
r = fetch(f'{BYBIT_URL}/kline?category=spot&symbol=POLUSDT&interval=D&start={TEST_TS}&limit=1')
pol_price = None
if isinstance(r, dict) and 'result' in r and r['result'].get('list'):
    lst = r['result']['list']
    if lst:
        row = lst[0]
        pol_price = {'open': float(row[1]), 'close': float(row[4]), 'ts_fmt': fmt(int(row[0]))}
        print(f'  open={pol_price["open"]}, close={pol_price["close"]}')
elif '__error__' in r:
    print(f'  ERROR: {r["__error__"]}')
result['pol_price'] = pol_price
time.sleep(SLEEP)

# 3. MATIC price at TEST_TS
print()
print(f'--- 3. MATICUSDT price at {fmt(TEST_TS)} ---')
r = fetch(f'{BYBIT_URL}/kline?category=spot&symbol=MATICUSDT&interval=D&start={TEST_TS}&limit=1')
matic_price = None
if isinstance(r, dict) and 'result' in r and r['result'].get('list'):
    lst = r['result']['list']
    if lst:
        row = lst[0]
        matic_price = {'open': float(row[1]), 'close': float(row[4]), 'ts_fmt': fmt(int(row[0]))}
        print(f'  open={matic_price["open"]}, close={matic_price["close"]}')
elif '__error__' in r:
    print(f'  ERROR: {r["__error__"]}')
result['matic_price'] = matic_price

# Interpretation
print()
print('=== Interpretation ===')
interp = 'unclear'
if pol_price and matic_price:
    diff_pct = abs(pol_price['close'] - matic_price['close']) / matic_price['close'] * 100
    print(f'  Close diff: {diff_pct:.1f}%')
    if diff_pct < 5:
        interp = 'same_asset'
        print(f'  → SAME ASSET (diff < 5%) — Bybit listed POL early with same price')
    elif diff_pct > 50:
        interp = 'different_asset'
        print(f'  → DIFFERENT ASSET (diff > 50%) — POL on Bybit is a different token')
    else:
        interp = 'unclear'
        print(f'  → UNCLEAR (5% < diff < 50%) — needs manual review')
elif not pol_price:
    interp = 'pol_not_available_at_test_date'
    print(f'  → POL not available at {fmt(TEST_TS)} on Bybit')
elif not matic_price:
    interp = 'matic_not_available_at_test_date'
    print(f'  → MATIC not available at {fmt(TEST_TS)} on Bybit')

result['interpretation'] = interp
result['test_date'] = fmt(TEST_TS)
result['test_ts'] = TEST_TS

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, 'w') as f:
    json.dump(result, f, indent=2, default=str)

print()
print(f'Output: {OUTPUT_FILE}')
print('=== POL Bybit COMPLETE ===')
