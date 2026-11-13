# MANIFEST.md — Self-Sufficient Test Registry

**Generated:** 2026-11-13T20:49:52Z
**Total files:** 130 | **PENDING (هنوز نگرفته):** 5

**Regenerate:** `bash tests/evidence/scan_repo.sh && python3 tests/evidence/gen_manifest.py`
**Manual edits فقط:** `triage.tsv` (tier/items) + `pending.tsv` (تست‌های نگرفته)

## §0 — Version Rule

| وضعیت | فایل |
|---|---|
| **معتبر (تست‌ها)** | این فایل (MANIFEST.md) |
| **مرجع دانش (R-Laws)** | docs/B_items/Cross_Item_Notes.md |
| **مرجع scope آیتم‌ها** | docs/MAP.md |
| **بازنویسی R-Laws** | Cross_Item_Notes (R-01..R-32) |
| Archive | v3.4_FINAL · v3.4.4_preview · v3.4.2_appendices · v2.1 · *.bak |


## §1 — T1-Core: In TEST_MAP (شاهد قطعی) (18 فایل)

| File | Item | Date | Summary |
|---|---|---|---|
| 2026-11-07_A4_OHLCV_Format.md | 07,08,10,16 | 2026-11-07 | 5 ناسازگاری OHLCV (field order، 4 ts format، float، direction، count) |
| 2026-11-07_migration_extract.md | 04 | 2026-11-07 | migration extract text |
| 7_no_data_resolved_2026-11-11.json | 03,15 | 2026-11-11 | 7 NO_DATA RESOLVED — all new assets no 2017 data |
| A6_A7_discovery_2026-11-08.json | 03,04 | 2026-11-08 | 3 migration + 3 delisted + KMNO |
| A6_A7_okx_correction_2026-11-09.json | 04 | 2026-11-09 | POL=2024-09-03 RENDER=2024-07-14 S=2025-01-20 (CONFIRMED) |
| a9_asset_start_dates_2026-11-08.json | 01,03,04,18 | 2026-11-08 | +04 (migration), +18 (price start) |
| a9_bitstamp_2026-11-11.json | 01 | 2026-11-11 | 85/150 TESTED (full run) |
| a9_coinbase_2026-11-11.json | 01,03,05 | 2026-11-11 | 99/150 usdt_usd_start=2021-05-04 22 Direct + 77 Converted |
| a9_okx_2026-11-09.json | 01,03 | 2026-11-09 | 105/150 TESTED USDT+USD+USDC |
| a9_okx_usdc_retry_2026-11-09.json | 01 | 2026-11-09 | 106/150 (+EURC) 600-day partial |
| a9_okx_v3_2026-11-09.json | 05,18 | 2026-11-09 | BTC-pair PENDING USD PENDING USDT 105/150 |
| asset_universe_master_2026-11-08.json | 03 | 2026-11-08 | 195 union |
| audit_2026-11-11.json | all | 2026-11-11 | 7 open questions answered — commit 8998ecf |
| cmc_top150_2026-11-08.json | 03 | 2026-11-08 | 150 CMC authoritative |
| final_125_supply.json | 03,15 | no-date | 118 tag FILLED |
| final_125_supply.json#2 | 03,15 | no-date | 118 tag FILLED |
| pol_bybit_test_2026-11-08.json | 04 | 2026-11-08 | same_asset close diff 0.14% launchTime=null test_date=2023-10-25 |
| supply_timeseries_2026-11-07.json | 12,15 | 2026-11-07 | 117 keys 13.17MB |

## §3 — T1-Driver Scripts (تولیدکننده شواهد) (15 فایل)

| File | Item | Date | Summary |
|---|---|---|---|
| a6_a7_discovery.py | 03,04 | no-date | produces A6_A7_discovery.json |
| a6_a7_okx_correction.py | 04 | no-date | produces A6_A7_okx_correction.json |
| a9_asset_start_dates.py | 01,03,04,18 | no-date | produces a9_asset_start_dates.json |
| a9_bitstamp_full.py | 01 | no-date | produces a9_bitstamp_11.json |
| a9_coinbase_full.py | 01,03,05 | no-date | produces a9_coinbase_11.json |
| a9_okx_only.py | 01,03 | no-date | produces a9_okx_2026-11-09.json |
| a9_okx_usdc_retry.py | 01 | no-date | produces a9_okx_usdc_retry.json |
| a9_okx_v3.py | 05,18 | no-date | produces a9_okx_v3.json |
| asset_master_builder.py | 03 | no-date | produces asset_universe_master.json |
| audit_2026-11-11.py | all | 2026-11-11 | produces audit_2026-11-11.json |
| bitstamp_diagnostic.py | 01 | no-date | script (was T1-core) |
| check_7_no_data_supply.py | 03,15 | no-date | produces 7_no_data_resolved.json |
| cmc_top150_fetch.py | 03 | no-date | produces cmc_top150.json |
| coinbase_btc_diagnostic.py | 01,05 | no-date | script (was T1-core) |
| pol_bybit_test.py | 04 | no-date | produces pol_bybit_test.json |

## §3b — T2: Active with Reconfirm (rate_limit ۲۹–۳۰ Oct) (17 فایل)

| File | Date | Summary |
|---|---|---|
| 2026-10-29_binance_klines_weight.txt | 2026-10-29 | weight=2 reset at minute boundary |
| 2026-10-29_binance_limit1000.txt | 2026-10-29 | Binance cap 1000 |
| 2026-10-29_binance_sol.txt | 2026-10-29 | Binance SOL cap |
| 2026-10-29_header_check.txt | 2026-10-29 | only Binance returns RL header |
| 2026-10-29_okx_safe.txt | 2026-10-29 | OKX safe |
| 2026-10-30_bitstamp_coinbase_cryptocom_safe.txt | 2026-10-30 | safe response |
| 2026-10-30_coinbase_websocket_all.txt | 2026-10-30 | 103 pairs 9659 msg/60s |
| 2026-10-30_okx_history_http.txt | 2026-10-30 | 2 req/s effective |
| 2026-10-30_okx_websocket_all.txt | 2026-10-30 | 89 pairs 1385 msg/60s confirm=0 |
| 2026-10-30_okx_websocket_test.txt | 2026-10-30 | OKX WS v1 |
| 2026-10-30_okx_websocket_test_v2.txt | 2026-10-30 | BTC 34 ETH 27 SOL 21 |
| A6_A7_discovery_2026-11-08_summary.md | 2026-11-08 | summary |
| a9_asset_start_dates_2026-11-08_summary.md | 2026-11-08 | summary |
| audit_2026-11-11.md | 2026-11-11 | summary mirror |
| cmc_internal_extended.yml | no-date | CMC extended workflow |
| final_supply_harvest.yml | no-date | data_source workflow (118 records) |
| test003_manual.yml | no-date | test003 workflow |

## §4 — T4 Helper Scripts (23 فایل)

| File | Date | Summary |
|---|---|---|
| __init__.py | no-date | TEST001 market-history MVP package. |
| adapters.py | no-date | TEST001 adapter — infra, not evidence |
| config.py | no-date | TEST001 config — infra, not evidence |
| create_item_registry.py | no-date | # Item_Registry.md — یادداشت‌های اختصاصی آیتم‌ها |
| final_clean_registry.py | no-date | — |
| fix_tmap_caveats.py | no-date | — |
| fix_tmap_caveats_v2.py | no-date | — |
| force_park_treasures.py | no-date | — |
| generate_appendices.py | no-date | v3.4.2 — Generate Appendix A/B/C (patched: a9_okx flat + exchanges Capital). |
| migrate_archive_content.py | no-date | — |
| park_legacy_treasures.py | no-date | ### [Legacy] محدودیت صرافی‌های خارج از Custom Range |
| patch_v34_3fix.py | no-date | v3.4 — 3 fixes (matching stripped format). |
| patch_v34_7fixes.py | no-date | v3.4 FINAL — 9 corrective patches (TD 5 + Extractor 4) |
| patch_v34_final.py | no-date | v3.4.5 FINAL — 19 patches (AM 7 + TD 9 + Extractor 3) with strict safety. |
| patch_v34_final_2.py | no-date | !/usr/bin/env python3 |
| patch_v34_full.py | no-date | v3.4.4 — FIX-4..7 + Appendix D (A6) + E (A4 schema). |
| patch_v34_session2.py | no-date | v3.4 FINAL — Session 2 patches (3 TD #13 + 5 R + 3 appends). |
| r07_patch_item12.py | no-date | — |
| remove_junk_exchanges.py | no-date | — |
| runner.py | no-date | TEST001 runner — infra, not evidence |
| update_tmap_bitstamp.py | no-date | — |
| update_tmap_coinbase.py | no-date | !/usr/bin/env python3 |
| validate_tmap.py | no-date | — |

## §5 — T4 Obsolete Workflows (15 فایل)

| File | Date | Summary |
|---|---|---|
| cmc_aggressive_fill.yml | no-date | — |
| cmc_earliest_dates.yml | no-date | — |
| cmc_fill_40.yml | no-date | — |
| combined_supply_tests.yml | no-date | — |
| fill_gaps.yml | no-date | — |
| test001_manual.yml | no-date | — |
| test_actions.yml | no-date | — |
| test_comprehensive_data.yml | no-date | — |
| test_cron_timing.yml | no-date | — |
| test_crypto2.yml | no-date | — |
| test_crypto2_v2.yml | no-date | — |
| test_external_api.yml | no-date | — |
| test_historical_supply.yml | no-date | — |
| verify_and_fill.yml | no-date | — |
| verify_top125_supply.yml | no-date | — |

## §6 — T4 Test Outputs (35 فایل)

| File | Date | Summary |
|---|---|---|
| aggressive_fill_29.json | no-date | FIGR_HELOC{1} · WBT{1} · RAIN{1} · CC{1} · BTW{1} · USYC{1} |
| cmc_fill_40.json | no-date | FIGR_HELOC{1} · HYPE{3} · WBT{1} · RAIN{1} · CC{1} · ENA{3} |
| cmc_ids.json | no-date | BTC=1 · ETH=1027 · USDT=825 · BNB=1839 · XRP=52 · USDC=3408 |
| coingecko_retry.json | no-date | FIGR_HELOC{2} · HYPE{2} · WBT{2} · RAIN{2} · CC{2} · ENA{2} |
| earliest_dates.json | no-date | 0G{3} · 1INCH{3} · 2Z{3} · A{3} · AAVE{3} · ADA{3} |
| fill_gaps_results.json | no-date | FIGR_HELOC{6} · HYPE{6} · USDS{6} · WBT{6} · RAIN{6} · CC{6} |
| latest_run.log | no-date | — |
| latest_run.log#10 | no-date | — |
| latest_run.log#11 | no-date | — |
| latest_run.log#12 | no-date | — |
| latest_run.log#13 | no-date | — |
| latest_run.log#14 | no-date | — |
| latest_run.log#15 | no-date | — |
| latest_run.log#16 | no-date | — |
| latest_run.log#17 | no-date | — |
| latest_run.log#18 | no-date | — |
| latest_run.log#2 | no-date | — |
| latest_run.log#3 | no-date | — |
| latest_run.log#4 | no-date | — |
| latest_run.log#5 | no-date | — |
| latest_run.log#6 | no-date | — |
| latest_run.log#7 | no-date | — |
| latest_run.log#8 | no-date | — |
| latest_run.log#9 | no-date | — |
| results.json | no-date | run_id=a0908f5c-5cec-4f36-83d6-3d07f0a5c744 · generated_at_utc=2026-10-17T16:47:20.978016Z · status=FAILED · assets_requ |
| results.json#2 | no-date | run_id=469a782f-fb10-48ff-a8fa-e42dcca1c5be · generated_at_utc=2026-10-17T17:05:34.092028Z · status=COMPLETED · assets_r |
| results.json#3 | no-date | run_id=b8edcf10-30fe-4bcd-8ca1-c8c5cd9c38f1 · generated_at_utc=2026-10-17T17:08:55.043110Z · status=PARTIAL · assets_req |
| results.json#4 | no-date | run_id=63a36de9-70c0-4ee7-8235-fe7d1f324078 · generated_at_utc=2026-10-17T21:15:13.392485Z · status=PARTIAL · assets_req |
| results.json#5 | no-date | run_id=f1bb1ec6-fe57-495f-b923-d7d5f9f4a292 · generated_at_utc=2026-10-17T22:08:21.322402Z · status=COMPLETED · assets_r |
| summary.txt | no-date | cmc_aggressive_fill.yml : OK cmc_earliest_dates.yml : OK cmc_fill_40.yml : OK cmc_internal_extended.yml : OK combined_su |
| supply_timeseries_2026-11-07_errors.json | 2026-11-07 | Item_15 USD1 502 error — reference |
| top125.json | no-date | list[125] |
| top125_mapped.json | no-date | list[125] |
| verification_results.json | no-date | list[125] |
| verify_125.json | no-date | list[125] |

## §8 — T3 Amateur Period (7 فایل)

| File | Date | Summary |
|---|---|---|
| 2026-10-27_requirements.txt | 2026-10-27 | requests |
| 2026-10-27_summary.txt | 2026-10-27 | ===== results/test001_manual/run_39050926831/test001-results/results.json ===== {"type":"object","keys":["assets","asset |
| 2026-10-28_5m_since_2017.tsv | 2026-10-28 | historical — superseded by A2 (7 Nov) |
| 2026-10-28_coverage_matrix.tsv | 2026-10-28 | historical — superseded by A9 composite |
| 2026-10-28_okx_cc_test.txt | 2026-10-28 | === Sanity: OKX reachable? === { "code": "0", "msg": "" } === Sanity: Crypto.com reachable? === 0 === OKX: 5m data exist |
| 2026-10-28_test_real_check.txt | 2026-10-28 | === 1. Binance BTCUSDT 5m — از 2017-08-17؟ === ✅ اولین کندل: 2017-08-17 04:00 UTC === 2. Binance ZECUSDT 5m — از 2021-01 |
| 2026-10-30_1h_1d_coverage.txt | 2026-10-30 | historical — superseded by A2.5a |

## §9 — Real Uncategorized (0 فایل)

_هیچ فایلی بدون طبقه‌بندی نیست_ ✅

## §10 — PENDING Tests (هنوز گرفته نشده) (5)

| Test | Item | P | Why |
|---|---|---|---|
| Bitstamp candle cap | 01,09 | P0 | سقف 300 تأیید نشده |
| Coinbase REST rate | 09 | P0 | GAP — هرگز تست نشد |
| C-019b (5-conn WS) | 09,11 | P0 | R-03 تصویب، تست نشده |
| WS Binance/Bybit | 11 | P1 | Part 2 v1.5 PROVISIONAL |
| USD1 DefiLlama | 15 | P3 | کم‌اولویت |
