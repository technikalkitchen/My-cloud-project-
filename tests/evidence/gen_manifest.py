#!/usr/bin/env python3
# gen_manifest.py — تولید MANIFEST.md از raw_tests.tsv + curated inline
import csv, datetime, os

RAW = "tests/evidence/raw_tests.tsv"
OUT = "docs/MANIFEST.md"

CURATED = {
    # T1 — Critical (19)
    "2026-11-07_A4_OHLCV_Format.md": ("T1","07,08,10,16","5 ناسازگاری OHLCV (field order، 4 ts format، float، direction، count)"),
    "A6_A7_discovery_2026-11-08.json": ("T1","03,04","3 migration + 3 delisted + KMNO"),
    "A6_A7_okx_correction_2026-11-09.json": ("T1","04","POL=2024-09-03 RENDER=2024-07-14 S=2025-01-20 (CONFIRMED)"),
    "pol_bybit_test_2026-11-08.json": ("T1","04","same_asset close diff 0.14% launchTime=null test_date=2023-10-25"),
    "a9_okx_2026-11-09.json": ("T1","01,03","105/150 TESTED USDT+USD+USDC"),
    "a9_okx_v3_2026-11-09.json": ("T1","05,18","BTC-pair PENDING USD PENDING USDT 105/150"),
    "a9_okx_usdc_retry_2026-11-09.json": ("T1","01","106/150 (+EURC) 600-day partial"),
    "a9_asset_start_dates_2026-11-08.json": ("T1","01,03","Binance 114/150 + Bybit 121/150 + Bitstamp 1/150 (composite)"),
    "a9_bitstamp_2026-11-11.json": ("T1","01","85/150 TESTED (full run)"),
    "a9_coinbase_2026-11-11.json": ("T1","01,03,05","99/150 usdt_usd_start=2021-05-04 22 Direct + 77 Converted"),
    "coinbase_btc_diagnostic.py": ("T1","01,05","9 tests — t2+t3 PASS — Full scan READY"),
    "bitstamp_diagnostic.py": ("T1","01","Bitstamp pair bug diagnostic"),
    "cmc_top150_2026-11-08.json": ("T1","03","150 CMC authoritative"),
    "asset_universe_master_2026-11-08.json": ("T1","03","195 union"),
    "audit_2026-11-11.json": ("T1","all","7 open questions answered — commit 8998ecf"),
    "7_no_data_resolved_2026-11-11.json": ("T1","03,15","7 NO_DATA RESOLVED — all new assets no 2017 data"),
    "2026-11-07_migration_extract.md": ("T1","04","migration extract text"),
    "supply_timeseries_2026-11-07.json": ("T1","12,15","117 keys 13.17MB"),
    "final_125_supply.json": ("T1","03,15","118 tag FILLED"),
    # T2 — Active (17)
    "2026-10-29_binance_klines_weight.txt": ("T2","09,11","weight=2 reset at minute boundary"),
    "2026-10-29_header_check.txt": ("T2","09","only Binance returns RL header"),
    "2026-10-29_okx_safe.txt": ("T2","09","OKX safe"),
    "2026-10-29_binance_limit1000.txt": ("T2","09","Binance cap 1000"),
    "2026-10-29_binance_sol.txt": ("T2","09","Binance SOL cap"),
    "2026-10-30_bitstamp_coinbase_cryptocom_safe.txt": ("T2","09","safe response"),
    "2026-10-30_coinbase_websocket_all.txt": ("T2","01,09,11","103 pairs 9659 msg/60s"),
    "2026-10-30_okx_history_http.txt": ("T2","09","2 req/s effective"),
    "2026-10-30_okx_websocket_all.txt": ("T2","01,09,11","89 pairs 1385 msg/60s confirm=0"),
    "2026-10-30_okx_websocket_test.txt": ("T2","09,11","OKX WS v1"),
    "2026-10-30_okx_websocket_test_v2.txt": ("T2","09,11","BTC 34 ETH 27 SOL 21"),
    "audit_2026-11-11.md": ("T2","all","summary mirror"),
    "A6_A7_discovery_2026-11-08_summary.md": ("T2","03,04","summary"),
    "a9_asset_start_dates_2026-11-08_summary.md": ("T2","01,03","summary"),
    "cmc_internal_extended.yml": ("T2","03","CMC extended workflow"),
    "test003_manual.yml": ("T2","13,16","test003 workflow"),
    "final_supply_harvest.yml": ("T2","15","data_source workflow (118 records)"),
    # T3 — Amateur (10)
    "2026-10-28_coverage_matrix.tsv": ("T3","03,16",""),
    "2026-10-28_5m_since_2017.tsv": ("T3","06,16",""),
    "2026-10-28_test_real_check.txt": ("T3","16",""),
    "2026-10-30_1h_1d_coverage.txt": ("T3","06,16",""),
    "2026-10-28_okx_cc_test.txt": ("T3","01",""),
    "2026-10-27_requirements.txt": ("T3","13",""),
    "2026-10-27_summary.txt": ("T3","13",""),
    "test001.py": ("T3","13,16",""),
    "test003_origin.py": ("T3","13",""),
    "test001_manual.yml": ("T3","13",""),
}

PENDING = [
    ("Bitstamp candle cap","01,09","P0","rate DONE، candle cap نه"),
    ("Coinbase REST rate","09","P0","GAP — هیچ‌جا نیست"),
    ("C-019b (5-conn WS)","09,11","P0","R-03 تصویب، تست نشده"),
    ("WS Binance/Bybit","11","P1","Part 2 v1.5 PROVISIONAL"),
    ("A2 TF test (no_commit)","06","P1","فایل شاهد ندارد — نیازمند بازنویسی TD (R-12b)"),
    ("A2.5a OKX 1d=2017-10-10","06","P1","no_commit — همان A2"),
    ("USD1 DefiLlama","15","P3","یک استیبل‌کوین"),
]

rows = []
with open(RAW, encoding="utf-8") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        rows.append(row)

tiers = {"T1":[],"T2":[],"T3":[],"T4":[]}
for row in rows:
    fn = row["filename"]
    if fn in CURATED:
        tier, items, result = CURATED[fn]
    else:
        tier, items, result = "T4","—",""
    tiers[tier].append({"path":row["path"],"fn":fn,"date":row["date"],
                         "inmap":row["in_test_map"],"items":items,"result":result})

now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
L = []
L.append("# MANIFEST.md — Self-Sufficient Test Registry")
L.append("")
L.append(f"**Generated:** {now} — auto-built, NOT handwritten")
L.append(f"**Total files:** {len(rows)} | **Source:** tests/evidence/raw_tests.tsv")
L.append("**Regenerate:** `bash tests/evidence/scan_repo.sh && python3 tests/evidence/gen_manifest.py`")
L.append("")
L.append("## §0 — Version Rule")
L.append("")
L.append("| وضعیت | فایل |")
L.append("|---|---|")
L.append("| معتبر | tests/TEST_MAP_v3.4_FINAL.md |")
L.append("| Archive | v3.4.2_appendices · v3.4.4_preview · TEST_MAP.md (v2.1) · *.bak-* |")
L.append("| ارجاع دیگر | PENDING — باید به v4 منتقل شود |")
L.append("")

for tier, title, note in [
    ("T1","§1 — T1: Critical (شاهد قطعی)","ستون فقرات نوشتن آیتم‌ها"),
    ("T2","§2 — T2: Active (فعال با caveat)","rate drift نمی‌کند، ولی behavior تطبیقی (Binance header) نیاز C-019b در Stage B"),
    ("T3","§3 — T3: Amateur (مرجع تاریخی)","دوره ۲۸–۳۰ Oct — نگه‌داری، ولی شاهد نیست"),
]:
    L.append(f"## {title}")
    L.append(""); L.append(f"_{note}_"); L.append("")
    L.append("| File | Path | Date | Items | In TEST_MAP | Result |")
    L.append("|---|---|---|---|---|---|")
    for e in sorted(tiers[tier], key=lambda x:x["fn"]):
        L.append(f"| {e['fn']} | `{e['path']}` | {e['date']} | {e['items']} | {e['inmap']} | {e['result']} |")
    L.append(""); L.append(f"**جمع {tier}: {len(tiers[tier])}**"); L.append("")

L.append("## §4 — T4: Archive / Non-Test")
L.append("")
L.append("_خروجی تست، workflow منسوخ، patch script — نه شاهد نوشتن آیتم._")
L.append("")
L.append("| File | Path | Date |")
L.append("|---|---|---|")
for e in sorted(tiers["T4"], key=lambda x:x["path"]):
    L.append(f"| {e['fn']} | `{e['path']}` | {e['date']} |")
L.append(""); L.append(f"**جمع T4: {len(tiers['T4'])}**"); L.append("")

L.append("## §5 — PENDING (نداریم، ولی لازم است)")
L.append("")
L.append("| Test | Items | P | Why |")
L.append("|---|---|---|---|")
for t,i,p,w in PENDING:
    L.append(f"| {t} | {i} | {p} | {w} |")
L.append(""); L.append(f"**جمع PENDING: {len(PENDING)}**"); L.append("")

total = sum(len(v) for v in tiers.values())
L.append("## §6 — Cross-Check")
L.append("")
L.append(f"- اسکن: {len(rows)}")
L.append(f"- T1={len(tiers['T1'])} T2={len(tiers['T2'])} T3={len(tiers['T3'])} T4={len(tiers['T4'])}")
L.append(f"- جمع: {total}")
L.append(f"- {'✅ Cross-check PASS' if total==len(rows) else '❌ FAIL: '+str(total)+'!='+str(len(rows))}")
L.append("")

L.append("## §7 — پوشش ۳۰ آیتم")
L.append("")
L.append("| Item | T1+T2 | PENDING |")
L.append("|---|---|---|")
for i in range(1,31):
    s = f"{i:02d}"
    c = sum(1 for t in ["T1","T2"] for e in tiers[t] if s in [x.strip() for x in e["items"].split(",")])
    pc = sum(1 for _,it,_,_ in PENDING if s in [x.strip() for x in it.split(",")])
    L.append(f"| Item_{s} | {c} | {pc} |")
L.append("")

os.makedirs("docs", exist_ok=True)
with open(OUT,"w",encoding="utf-8") as f:
    f.write("\n".join(L))

print(f"✅ {OUT}")
print(f"   خطوط: {len(L)}")
print(f"   T1={len(tiers['T1'])} T2={len(tiers['T2'])} T3={len(tiers['T3'])} T4={len(tiers['T4'])}")
print(f"   Cross-check: {total}/{len(rows)}")
