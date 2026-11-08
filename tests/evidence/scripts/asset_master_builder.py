import json
import os
import sys

UNIVERSE_FILE = 'data/test001/universe.json'
SUPPLY_FILE = 'results/final_supply_harvest/run_40351779336/final-125-supply-results/final_125_supply.json'
DISCOVERY_FILE = 'tests/evidence/A6_A7_discovery_2026-11-08.json'
OUTPUT_FILE = 'tests/evidence/asset_universe_master_2026-11-08.json'

def load_json(path):
    if not os.path.exists(path):
        print(f'WARNING: {path} not found')
        return None
    with open(path) as f:
        return json.load(f)

def add_asset(assets, symbol, reason, cmc_id=None, source=None):
    if not symbol:
        return
    if symbol not in assets:
        assets[symbol] = {'sources': [], 'reasons': [], 'cmc_ids': []}
    a = assets[symbol]
    if source and source not in a['sources']:
        a['sources'].append(source)
    if reason not in a['reasons']:
        a['reasons'].append(reason)
    if cmc_id and cmc_id not in a['cmc_ids']:
        a['cmc_ids'].append(cmc_id)

print('=== Asset Master Builder ===')
print()

assets = {}

universe = load_json(UNIVERSE_FILE)
if universe:
    for item in universe.get('assets', []):
        sym = item.get('symbol') or item
        add_asset(assets, sym, 'in_universe_125', source='universe')
    print(f'Universe: {len(universe.get("assets", []))}')

supply = load_json(SUPPLY_FILE)
if supply:
    filled = 0
    for item in supply:
        if item.get('status') == 'FILLED':
            add_asset(assets, item['symbol'], 'filled_supply', cmc_id=item.get('cmc_id'), source='supply_125')
            filled += 1
    print(f'Supply FILLED: {filled}')

discovery = load_json(DISCOVERY_FILE)
if discovery:
    for m in discovery.get('migrations', []):
        add_asset(assets, m.get('from_symbol'), 'migration_source', cmc_id=m.get('from_cmc_id'), source='discovery')
        add_asset(assets, m.get('to_symbol'), 'migration_target', cmc_id=m.get('to_cmc_id'), source='discovery')
    for d in discovery.get('delisted', []):
        add_asset(assets, d.get('symbol'), 'delisted_known', cmc_id=d.get('cmc_id'), source='discovery')
    for s in discovery.get('survivors', []):
        add_asset(assets, s.get('symbol'), 'survivor_known', cmc_id=s.get('cmc_id'), source='discovery')
    print(f'Migrations: {len(discovery.get("migrations", []))}, Delisted: {len(discovery.get("delisted", []))}, Survivors: {len(discovery.get("survivors", []))}')

by_reason = {}
for sym, data in assets.items():
    for r in data['reasons']:
        by_reason.setdefault(r, []).append(sym)

summary = {
    'total_unique_assets': len(assets),
    'by_reason_counts': {k: len(v) for k, v in by_reason.items()},
    'assets': assets,
}

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, 'w') as f:
    json.dump(summary, f, indent=2, default=str)

print()
print('=== Summary ===')
print(f'Total unique assets: {len(assets)}')
for k, v in sorted(summary['by_reason_counts'].items()):
    print(f'  {k}: {v}')
print(f'Output: {OUTPUT_FILE}')
print('=== Asset Master COMPLETE ===')

