# TEST_MAP_v4.md — Item-Centric Test Registry

**Generated:** auto from `docs/MANIFEST.md` + `tests/evidence/triage.tsv` + `pending.tsv`
**Regenerate:** `python3 tests/evidence/gen_test_map_v4.py`

**Complement:** `docs/MANIFEST.md` = File → Items · This file = Item → Files

---

## §0 — Cross-Cutting Files (apply to all items)

| File | Tier | Date | Summary |
|---|---|---|---|
| audit_2026-11-11.json | T1-core | 2026-11-11 | 7 open questions answered — commit 8998ecf |
| audit_2026-11-11.md | T2 | 2026-11-11 | summary mirror |
| audit_2026-11-11.py | T1-driver | 2026-11-11 | produces audit_2026-11-11.json |

---

## Item_01 — Exchanges

### Tests

| Tier | File | Date | Summary |
|---|---|---|---|
| T1-core | a9_asset_start_dates_2026-11-08.json | 2026-11-08 | +04 (migration), +18 (price start) |
| T1-core | a9_bitstamp_2026-11-11.json | 2026-11-11 | 85/150 TESTED (full run) |
| T1-core | a9_coinbase_2026-11-11.json | 2026-11-11 | 99/150 usdt_usd_start=2021-05-04 22 Direct + 77 Converted |
| T1-core | a9_okx_2026-11-09.json | 2026-11-09 | 105/150 TESTED USDT+USD+USDC |
| T1-core | a9_okx_usdc_retry_2026-11-09.json | 2026-11-09 | 106/150 (+EURC) 600-day partial |
| T1-driver | a9_asset_start_dates.py | no-date | produces a9_asset_start_dates.json |
| T1-driver | a9_bitstamp_full.py | no-date | produces a9_bitstamp_11.json |
| T1-driver | a9_coinbase_full.py | no-date | produces a9_coinbase_11.json |
| T1-driver | a9_okx_only.py | no-date | produces a9_okx_2026-11-09.json |
| T1-driver | a9_okx_usdc_retry.py | no-date | produces a9_okx_usdc_retry.json |
| T1-driver | bitstamp_diagnostic.py | no-date | script (was T1-core) |
| T1-driver | coinbase_btc_diagnostic.py | no-date | script (was T1-core) |
| T2 | 2026-10-30_coinbase_websocket_all.txt | 2026-10-30 | 103 pairs 9659 msg/60s |
| T2 | 2026-10-30_okx_websocket_all.txt | 2026-10-30 | 89 pairs 1385 msg/60s confirm=0 |
| T2 | a9_asset_start_dates_2026-11-08_summary.md | 2026-11-08 | summary |

### PENDING

| Test | Priority | Why |
|---|---|---|
| Bitstamp candle cap | P0 | سقف 300 تأیید نشده |

---

## Item_02 — Aggregators

_هیچ تستی ندارد_

---

## Item_03 — Universe

### Tests

| Tier | File | Date | Summary |
|---|---|---|---|
| T1-core | 7_no_data_resolved_2026-11-11.json | 2026-11-11 | 7 NO_DATA RESOLVED — all new assets no 2017 data |
| T1-core | A6_A7_discovery_2026-11-08.json | 2026-11-08 | 3 migration + 3 delisted + KMNO |
| T1-core | a9_asset_start_dates_2026-11-08.json | 2026-11-08 | +04 (migration), +18 (price start) |
| T1-core | a9_coinbase_2026-11-11.json | 2026-11-11 | 99/150 usdt_usd_start=2021-05-04 22 Direct + 77 Converted |
| T1-core | a9_okx_2026-11-09.json | 2026-11-09 | 105/150 TESTED USDT+USD+USDC |
| T1-core | asset_universe_master_2026-11-08.json | 2026-11-08 | 195 union |
| T1-core | cmc_top150_2026-11-08.json | 2026-11-08 | 150 CMC authoritative |
| T1-core | final_125_supply.json | no-date | 118 tag FILLED |
| T1-driver | a6_a7_discovery.py | no-date | produces A6_A7_discovery.json |
| T1-driver | a9_asset_start_dates.py | no-date | produces a9_asset_start_dates.json |
| T1-driver | a9_coinbase_full.py | no-date | produces a9_coinbase_11.json |
| T1-driver | a9_okx_only.py | no-date | produces a9_okx_2026-11-09.json |
| T1-driver | asset_master_builder.py | no-date | produces asset_universe_master.json |
| T1-driver | check_7_no_data_supply.py | no-date | produces 7_no_data_resolved.json |
| T1-driver | cmc_top150_fetch.py | no-date | produces cmc_top150.json |
| T2 | A6_A7_discovery_2026-11-08_summary.md | 2026-11-08 | summary |
| T2 | a9_asset_start_dates_2026-11-08_summary.md | 2026-11-08 | summary |
| T2 | cmc_internal_extended.yml | no-date | CMC extended workflow |

---

## Item_04 — Migration Map

### Tests

| Tier | File | Date | Summary |
|---|---|---|---|
| T1-core | 2026-11-07_migration_extract.md | 2026-11-07 | migration extract text |
| T1-core | A6_A7_discovery_2026-11-08.json | 2026-11-08 | 3 migration + 3 delisted + KMNO |
| T1-core | A6_A7_okx_correction_2026-11-09.json | 2026-11-09 | POL=2024-09-03 RENDER=2024-07-14 S=2025-01-20 (CONFIRMED) |
| T1-core | a9_asset_start_dates_2026-11-08.json | 2026-11-08 | +04 (migration), +18 (price start) |
| T1-core | pol_bybit_test_2026-11-08.json | 2026-11-08 | same_asset close diff 0.14% launchTime=null test_date=2023-10-25 |
| T1-driver | a6_a7_discovery.py | no-date | produces A6_A7_discovery.json |
| T1-driver | a6_a7_okx_correction.py | no-date | produces A6_A7_okx_correction.json |
| T1-driver | a9_asset_start_dates.py | no-date | produces a9_asset_start_dates.json |
| T1-driver | pol_bybit_test.py | no-date | produces pol_bybit_test.json |
| T2 | A6_A7_discovery_2026-11-08_summary.md | 2026-11-08 | summary |

---

## Item_05 — Canonical Pairs

### Tests

| Tier | File | Date | Summary |
|---|---|---|---|
| T1-core | a9_coinbase_2026-11-11.json | 2026-11-11 | 99/150 usdt_usd_start=2021-05-04 22 Direct + 77 Converted |
| T1-core | a9_okx_v3_2026-11-09.json | 2026-11-09 | BTC-pair PENDING USD PENDING USDT 105/150 |
| T1-driver | a9_coinbase_full.py | no-date | produces a9_coinbase_11.json |
| T1-driver | a9_okx_v3.py | no-date | produces a9_okx_v3.json |
| T1-driver | coinbase_btc_diagnostic.py | no-date | script (was T1-core) |

---

## Item_06 — Timeframes

_هیچ تستی ندارد_

---

## Item_07 — Precision & Time

### Tests

| Tier | File | Date | Summary |
|---|---|---|---|
| T1-core | 2026-11-07_A4_OHLCV_Format.md | 2026-11-07 | 5 ناسازگاری OHLCV (field order، 4 ts format، float، direction، count) |

---

## Item_08 — Data Contract

### Tests

| Tier | File | Date | Summary |
|---|---|---|---|
| T1-core | 2026-11-07_A4_OHLCV_Format.md | 2026-11-07 | 5 ناسازگاری OHLCV (field order، 4 ts format، float، direction، count) |

---

## Item_09 — Rate Limit

### Tests

| Tier | File | Date | Summary |
|---|---|---|---|
| T2 | 2026-10-29_binance_klines_weight.txt | 2026-10-29 | weight=2 reset at minute boundary |
| T2 | 2026-10-29_binance_limit1000.txt | 2026-10-29 | Binance cap 1000 |
| T2 | 2026-10-29_binance_sol.txt | 2026-10-29 | Binance SOL cap |
| T2 | 2026-10-29_header_check.txt | 2026-10-29 | only Binance returns RL header |
| T2 | 2026-10-29_okx_safe.txt | 2026-10-29 | OKX safe |
| T2 | 2026-10-30_bitstamp_coinbase_cryptocom_safe.txt | 2026-10-30 | safe response |
| T2 | 2026-10-30_coinbase_websocket_all.txt | 2026-10-30 | 103 pairs 9659 msg/60s |
| T2 | 2026-10-30_okx_history_http.txt | 2026-10-30 | 2 req/s effective |
| T2 | 2026-10-30_okx_websocket_all.txt | 2026-10-30 | 89 pairs 1385 msg/60s confirm=0 |
| T2 | 2026-10-30_okx_websocket_test.txt | 2026-10-30 | OKX WS v1 |
| T2 | 2026-10-30_okx_websocket_test_v2.txt | 2026-10-30 | BTC 34 ETH 27 SOL 21 |

### PENDING

| Test | Priority | Why |
|---|---|---|
| Bitstamp candle cap | P0 | سقف 300 تأیید نشده |
| Coinbase REST rate | P0 | GAP — هرگز تست نشد |
| C-019b (5-conn WS) | P0 | R-03 تصویب، تست نشده |

---

## Item_10 — Error

### Tests

| Tier | File | Date | Summary |
|---|---|---|---|
| T1-core | 2026-11-07_A4_OHLCV_Format.md | 2026-11-07 | 5 ناسازگاری OHLCV (field order، 4 ts format، float، direction، count) |

---

## Item_11 — Cache

### Tests

| Tier | File | Date | Summary |
|---|---|---|---|
| T2 | 2026-10-29_binance_klines_weight.txt | 2026-10-29 | weight=2 reset at minute boundary |
| T2 | 2026-10-30_coinbase_websocket_all.txt | 2026-10-30 | 103 pairs 9659 msg/60s |
| T2 | 2026-10-30_okx_websocket_all.txt | 2026-10-30 | 89 pairs 1385 msg/60s confirm=0 |
| T2 | 2026-10-30_okx_websocket_test.txt | 2026-10-30 | OKX WS v1 |
| T2 | 2026-10-30_okx_websocket_test_v2.txt | 2026-10-30 | BTC 34 ETH 27 SOL 21 |

### PENDING

| Test | Priority | Why |
|---|---|---|
| C-019b (5-conn WS) | P0 | R-03 تصویب، تست نشده |
| WS Binance/Bybit | P1 | Part 2 v1.5 PROVISIONAL |

---

## Item_12 — Storage

### Tests

| Tier | File | Date | Summary |
|---|---|---|---|
| T1-core | supply_timeseries_2026-11-07.json | 2026-11-07 | 117 keys 13.17MB |

---

## Item_13 — Bootstrap

### Tests

| Tier | File | Date | Summary |
|---|---|---|---|
| T2 | test003_manual.yml | no-date | test003 workflow |

---

## Item_14 — Incremental

_هیچ تستی ندارد_

---

## Item_15 — Supply

### Tests

| Tier | File | Date | Summary |
|---|---|---|---|
| T1-core | 7_no_data_resolved_2026-11-11.json | 2026-11-11 | 7 NO_DATA RESOLVED — all new assets no 2017 data |
| T1-core | final_125_supply.json | no-date | 118 tag FILLED |
| T1-core | supply_timeseries_2026-11-07.json | 2026-11-07 | 117 keys 13.17MB |
| T1-driver | check_7_no_data_supply.py | no-date | produces 7_no_data_resolved.json |
| T2 | final_supply_harvest.yml | no-date | data_source workflow (118 records) |

### PENDING

| Test | Priority | Why |
|---|---|---|
| USD1 DefiLlama | P3 | کم‌اولویت |

---

## Item_16 — OHLCV

### Tests

| Tier | File | Date | Summary |
|---|---|---|---|
| T1-core | 2026-11-07_A4_OHLCV_Format.md | 2026-11-07 | 5 ناسازگاری OHLCV (field order، 4 ts format، float، direction، count) |
| T2 | test003_manual.yml | no-date | test003 workflow |

---

## Item_17 — Exchange Volume

_هیچ تستی ندارد_

---

## Item_18 — Exchange Price

### Tests

| Tier | File | Date | Summary |
|---|---|---|---|
| T1-core | a9_asset_start_dates_2026-11-08.json | 2026-11-08 | +04 (migration), +18 (price start) |
| T1-core | a9_okx_v3_2026-11-09.json | 2026-11-09 | BTC-pair PENDING USD PENDING USDT 105/150 |
| T1-driver | a9_asset_start_dates.py | no-date | produces a9_asset_start_dates.json |
| T1-driver | a9_okx_v3.py | no-date | produces a9_okx_v3.json |

---

## Item_19 — Exchange MC

_هیچ تستی ندارد_

---

## Item_20 — Exchange Reliability

_هیچ تستی ندارد_

---

## Item_21 — Data Reliability

_هیچ تستی ندارد_

---

## Item_22 — Exchange Dominance

_هیچ تستی ندارد_

---

## Item_23 — Kitchen Price

_هیچ تستی ندارد_

---

## Item_24 — Kitchen Volume

_هیچ تستی ندارد_

---

## Item_25 — Kitchen MC

_هیچ تستی ندارد_

---

## Item_26 — Kitchen Coverage

_هیچ تستی ندارد_

---

## Item_27 — Ranking

_هیچ تستی ندارد_

---

## Item_28 — Grouping

_هیچ تستی ندارد_

---

## Item_29 — Kitchen Dominance

_هیچ تستی ندارد_

---

## Item_30 — Snapshot

_هیچ تستی ندارد_

---

## §31 — Summary

- **Items with tests:** 14/30
- **Items without tests:** 16/30
- **Total file-assignments:** 80
- **PENDING tests:** 7
- **Cross-cutting:** 3

### Items بدون تست

- **Item_02** (Aggregators)
- **Item_06** (Timeframes)
- **Item_14** (Incremental)
- **Item_17** (Exchange Volume)
- **Item_19** (Exchange MC)
- **Item_20** (Exchange Reliability)
- **Item_21** (Data Reliability)
- **Item_22** (Exchange Dominance)
- **Item_23** (Kitchen Price)
- **Item_24** (Kitchen Volume)
- **Item_25** (Kitchen MC)
- **Item_26** (Kitchen Coverage)
- **Item_27** (Ranking)
- **Item_28** (Grouping)
- **Item_29** (Kitchen Dominance)
- **Item_30** (Snapshot)
