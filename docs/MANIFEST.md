# MANIFEST.md — Self-Sufficient Test Registry

**Generated:** 2026-11-13T16:48:13Z — auto-built, NOT handwritten
**Total files:** 135 | **Source:** tests/evidence/raw_tests.tsv
**Regenerate:** `bash tests/evidence/scan_repo.sh && python3 tests/evidence/gen_manifest.py`

## §0 — Version Rule

| وضعیت | فایل |
|---|---|
| معتبر | tests/TEST_MAP_v3.4_FINAL.md |
| Archive | v3.4.2_appendices · v3.4.4_preview · TEST_MAP.md (v2.1) · *.bak-* |
| ارجاع دیگر | PENDING — باید به v4 منتقل شود |

## §1 — T1: Critical (شاهد قطعی)

_ستون فقرات نوشتن آیتم‌ها_

| File | Path | Date | Items | In TEST_MAP | Result |
|---|---|---|---|---|---|
| 2026-11-07_A4_OHLCV_Format.md | `tests/evidence/2026-11-07_A4_OHLCV_Format.md` | 2026-11-07 | 07,08,10,16 | YES | 5 ناسازگاری OHLCV (field order، 4 ts format، float، direction، count) |
| 2026-11-07_migration_extract.md | `tests/evidence/A6/2026-11-07_migration_extract.md` | 2026-11-07 | 04 | NO | migration extract text |
| 7_no_data_resolved_2026-11-11.json | `tests/evidence/7_no_data_resolved_2026-11-11.json` | 2026-11-11 | 03,15 | NO | 7 NO_DATA RESOLVED — all new assets no 2017 data |
| A6_A7_discovery_2026-11-08.json | `tests/evidence/A6_A7_discovery_2026-11-08.json` | 2026-11-08 | 03,04 | YES | 3 migration + 3 delisted + KMNO |
| A6_A7_okx_correction_2026-11-09.json | `tests/evidence/A6_A7_okx_correction_2026-11-09.json` | 2026-11-09 | 04 | YES | POL=2024-09-03 RENDER=2024-07-14 S=2025-01-20 (CONFIRMED) |
| a9_asset_start_dates_2026-11-08.json | `tests/evidence/a9_asset_start_dates_2026-11-08.json` | 2026-11-08 | 01,03 | YES | Binance 114/150 + Bybit 121/150 + Bitstamp 1/150 (composite) |
| a9_bitstamp_2026-11-11.json | `tests/evidence/a9_bitstamp_2026-11-11.json` | 2026-11-11 | 01 | NO | 85/150 TESTED (full run) |
| a9_coinbase_2026-11-11.json | `tests/evidence/a9_coinbase_2026-11-11.json` | 2026-11-11 | 01,03,05 | NO | 99/150 usdt_usd_start=2021-05-04 22 Direct + 77 Converted |
| a9_okx_2026-11-09.json | `tests/evidence/a9_okx_2026-11-09.json` | 2026-11-09 | 01,03 | YES | 105/150 TESTED USDT+USD+USDC |
| a9_okx_usdc_retry_2026-11-09.json | `tests/evidence/a9_okx_usdc_retry_2026-11-09.json` | 2026-11-09 | 01 | YES | 106/150 (+EURC) 600-day partial |
| a9_okx_v3_2026-11-09.json | `tests/evidence/a9_okx_v3_2026-11-09.json` | 2026-11-09 | 05,18 | YES | BTC-pair PENDING USD PENDING USDT 105/150 |
| asset_universe_master_2026-11-08.json | `tests/evidence/asset_universe_master_2026-11-08.json` | 2026-11-08 | 03 | YES | 195 union |
| audit_2026-11-11.json | `tests/evidence/audit_2026-11-11.json` | 2026-11-11 | all | YES | 7 open questions answered — commit 8998ecf |
| bitstamp_diagnostic.py | `tests/evidence/scripts/bitstamp_diagnostic.py` | no-date | 01 | NO | Bitstamp pair bug diagnostic |
| cmc_top150_2026-11-08.json | `tests/evidence/cmc_top150_2026-11-08.json` | 2026-11-08 | 03 | YES | 150 CMC authoritative |
| coinbase_btc_diagnostic.py | `tests/evidence/scripts/coinbase_btc_diagnostic.py` | no-date | 01,05 | YES | 9 tests — t2+t3 PASS — Full scan READY |
| final_125_supply.json | `results/final_supply_harvest/run_40351779336/final-125-supply-results/final_125_supply.json` | no-date | 03,15 | YES | 118 tag FILLED |
| final_125_supply.json | `results/run_40351779336/final-125-supply-results/final_125_supply.json` | no-date | 03,15 | YES | 118 tag FILLED |
| pol_bybit_test_2026-11-08.json | `tests/evidence/pol_bybit_test_2026-11-08.json` | 2026-11-08 | 04 | YES | same_asset close diff 0.14% launchTime=null test_date=2023-10-25 |
| supply_timeseries_2026-11-07.json | `results/supply_timeseries/supply_timeseries_2026-11-07.json` | 2026-11-07 | 12,15 | YES | 117 keys 13.17MB |

**جمع T1: 20**

## §2 — T2: Active (فعال با caveat)

_rate drift نمی‌کند، ولی behavior تطبیقی (Binance header) نیاز C-019b در Stage B_

| File | Path | Date | Items | In TEST_MAP | Result |
|---|---|---|---|---|---|
| 2026-10-29_binance_klines_weight.txt | `tests/rate_limit/2026-10-29_binance_klines_weight.txt` | 2026-10-29 | 09,11 | NO | weight=2 reset at minute boundary |
| 2026-10-29_binance_limit1000.txt | `tests/rate_limit/2026-10-29_binance_limit1000.txt` | 2026-10-29 | 09 | NO | Binance cap 1000 |
| 2026-10-29_binance_sol.txt | `tests/rate_limit/2026-10-29_binance_sol.txt` | 2026-10-29 | 09 | NO | Binance SOL cap |
| 2026-10-29_header_check.txt | `tests/rate_limit/2026-10-29_header_check.txt` | 2026-10-29 | 09 | NO | only Binance returns RL header |
| 2026-10-29_okx_safe.txt | `tests/rate_limit/2026-10-29_okx_safe.txt` | 2026-10-29 | 09 | NO | OKX safe |
| 2026-10-30_bitstamp_coinbase_cryptocom_safe.txt | `tests/rate_limit/2026-10-30_bitstamp_coinbase_cryptocom_safe.txt` | 2026-10-30 | 09 | NO | safe response |
| 2026-10-30_coinbase_websocket_all.txt | `tests/rate_limit/2026-10-30_coinbase_websocket_all.txt` | 2026-10-30 | 01,09,11 | NO | 103 pairs 9659 msg/60s |
| 2026-10-30_okx_history_http.txt | `tests/rate_limit/2026-10-30_okx_history_http.txt` | 2026-10-30 | 09 | NO | 2 req/s effective |
| 2026-10-30_okx_websocket_all.txt | `tests/rate_limit/2026-10-30_okx_websocket_all.txt` | 2026-10-30 | 01,09,11 | NO | 89 pairs 1385 msg/60s confirm=0 |
| 2026-10-30_okx_websocket_test.txt | `tests/rate_limit/2026-10-30_okx_websocket_test.txt` | 2026-10-30 | 09,11 | NO | OKX WS v1 |
| 2026-10-30_okx_websocket_test_v2.txt | `tests/rate_limit/2026-10-30_okx_websocket_test_v2.txt` | 2026-10-30 | 09,11 | NO | BTC 34 ETH 27 SOL 21 |
| A6_A7_discovery_2026-11-08_summary.md | `tests/evidence/A6_A7_discovery_2026-11-08_summary.md` | 2026-11-08 | 03,04 | NO | summary |
| a9_asset_start_dates_2026-11-08_summary.md | `tests/evidence/a9_asset_start_dates_2026-11-08_summary.md` | 2026-11-08 | 01,03 | NO | summary |
| audit_2026-11-11.md | `tests/evidence/audit_2026-11-11.md` | 2026-11-11 | all | NO | summary mirror |
| cmc_internal_extended.yml | `.github/workflows/cmc_internal_extended.yml` | no-date | 03 | NO | CMC extended workflow |
| final_supply_harvest.yml | `.github/workflows/final_supply_harvest.yml` | no-date | 15 | YES | data_source workflow (118 records) |
| test003_manual.yml | `.github/workflows/test003_manual.yml` | no-date | 13,16 | NO | test003 workflow |

**جمع T2: 17**

## §3 — T3: Amateur (مرجع تاریخی)

_دوره ۲۸–۳۰ Oct — نگه‌داری، ولی شاهد نیست_

| File | Path | Date | Items | In TEST_MAP | Result |
|---|---|---|---|---|---|
| 2026-10-27_requirements.txt | `tests/legacy_test001/2026-10-27_requirements.txt` | 2026-10-27 | 13 | NO |  |
| 2026-10-27_summary.txt | `tests/legacy_test001/2026-10-27_summary.txt` | 2026-10-27 | 13 | NO |  |
| 2026-10-28_5m_since_2017.tsv | `tests/coverage/2026-10-28_5m_since_2017.tsv` | 2026-10-28 | 06,16 | NO |  |
| 2026-10-28_coverage_matrix.tsv | `tests/coverage/2026-10-28_coverage_matrix.tsv` | 2026-10-28 | 03,16 | NO |  |
| 2026-10-28_okx_cc_test.txt | `tests/coverage/2026-10-28_okx_cc_test.txt` | 2026-10-28 | 01 | NO |  |
| 2026-10-28_test_real_check.txt | `tests/coverage/2026-10-28_test_real_check.txt` | 2026-10-28 | 16 | NO |  |
| 2026-10-30_1h_1d_coverage.txt | `tests/coverage/2026-10-30_1h_1d_coverage.txt` | 2026-10-30 | 06,16 | NO |  |
| test001_manual.yml | `.github/workflows/test001_manual.yml` | no-date | 13 | YES |  |

**جمع T3: 8**

## §4 — T4: Archive / Non-Test

_خروجی تست، workflow منسوخ، patch script — نه شاهد نوشتن آیتم._

| File | Path | Date |
|---|---|---|
| cmc_aggressive_fill.yml | `.github/workflows/cmc_aggressive_fill.yml` | no-date |
| cmc_earliest_dates.yml | `.github/workflows/cmc_earliest_dates.yml` | no-date |
| cmc_fill_40.yml | `.github/workflows/cmc_fill_40.yml` | no-date |
| combined_supply_tests.yml | `.github/workflows/combined_supply_tests.yml` | no-date |
| fill_gaps.yml | `.github/workflows/fill_gaps.yml` | no-date |
| test_actions.yml | `.github/workflows/test_actions.yml` | no-date |
| test_comprehensive_data.yml | `.github/workflows/test_comprehensive_data.yml` | no-date |
| test_cron_timing.yml | `.github/workflows/test_cron_timing.yml` | no-date |
| test_crypto2.yml | `.github/workflows/test_crypto2.yml` | no-date |
| test_crypto2_v2.yml | `.github/workflows/test_crypto2_v2.yml` | no-date |
| test_external_api.yml | `.github/workflows/test_external_api.yml` | no-date |
| test_historical_supply.yml | `.github/workflows/test_historical_supply.yml` | no-date |
| verify_and_fill.yml | `.github/workflows/verify_and_fill.yml` | no-date |
| verify_top125_supply.yml | `.github/workflows/verify_top125_supply.yml` | no-date |
| __init__.py | `app/market/test001/__init__.py` | no-date |
| adapters.py | `app/market/test001/adapters.py` | no-date |
| config.py | `app/market/test001/config.py` | no-date |
| runner.py | `app/market/test001/runner.py` | no-date |
| latest_run.log | `results/cmc_aggressive_fill/latest_run.log` | no-date |
| aggressive_fill_29.json | `results/cmc_aggressive_fill/run_40350363383/aggressive-fill-results/aggressive_fill_29.json` | no-date |
| latest_run.log | `results/cmc_earliest_dates/latest_run.log` | no-date |
| cmc_ids.json | `results/cmc_earliest_dates/run_40238238190/earliest-dates/cmc_ids.json` | no-date |
| earliest_dates.json | `results/cmc_earliest_dates/run_40238238190/earliest-dates/earliest_dates.json` | no-date |
| latest_run.log | `results/cmc_fill_40/latest_run.log` | no-date |
| cmc_fill_40.json | `results/cmc_fill_40/run_40347826878/cmc-fill-40-results/cmc_fill_40.json` | no-date |
| latest_run.log | `results/cmc_internal_extended/latest_run.log` | no-date |
| latest_run.log | `results/combined_supply_tests/latest_run.log` | no-date |
| latest_run.log | `results/fill_gaps/latest_run.log` | no-date |
| fill_gaps_results.json | `results/fill_gaps/run_40332035054/fill-gaps-results/fill_gaps_results.json` | no-date |
| latest_run.log | `results/final_supply_harvest/latest_run.log` | no-date |
| summary.txt | `results/summary.txt` | no-date |
| supply_timeseries_2026-11-07_errors.json | `results/supply_timeseries/supply_timeseries_2026-11-07_errors.json` | 2026-11-07 |
| latest_run.log | `results/test001_manual/latest_run.log` | no-date |
| results.json | `results/test001_manual/run_39050926831/test001-results/results.json` | no-date |
| results.json | `results/test001_manual/run_39052224713/test001-results/results.json` | no-date |
| results.json | `results/test001_manual/run_39052463360/test001-results/results.json` | no-date |
| results.json | `results/test001_manual/run_39070141142/test001-results/results.json` | no-date |
| results.json | `results/test001_manual/run_39073819201/test001-results/results.json` | no-date |
| latest_run.log | `results/test003_manual/latest_run.log` | no-date |
| latest_run.log | `results/test_actions/latest_run.log` | no-date |
| latest_run.log | `results/test_comprehensive_data/latest_run.log` | no-date |
| latest_run.log | `results/test_cron_timing/latest_run.log` | no-date |
| latest_run.log | `results/test_crypto2/latest_run.log` | no-date |
| latest_run.log | `results/test_crypto2_v2/latest_run.log` | no-date |
| latest_run.log | `results/test_external_api/latest_run.log` | no-date |
| latest_run.log | `results/test_historical_supply/latest_run.log` | no-date |
| latest_run.log | `results/verify_and_fill/latest_run.log` | no-date |
| coingecko_retry.json | `results/verify_and_fill/run_40335328998/verify-125-results/coingecko_retry.json` | no-date |
| verify_125.json | `results/verify_and_fill/run_40335328998/verify-125-results/verify_125.json` | no-date |
| latest_run.log | `results/verify_top125_supply/latest_run.log` | no-date |
| top125.json | `results/verify_top125_supply/run_40239205961/top125-verification/top125.json` | no-date |
| top125_mapped.json | `results/verify_top125_supply/run_40239205961/top125-verification/top125_mapped.json` | no-date |
| verification_results.json | `results/verify_top125_supply/run_40239205961/top125-verification/verification_results.json` | no-date |
| raw_tests.tsv | `tests/evidence/raw_tests.tsv` | no-date |
| scan_repo.sh | `tests/evidence/scan_repo.sh` | no-date |
| a6_a7_discovery.py | `tests/evidence/scripts/a6_a7_discovery.py` | no-date |
| a6_a7_okx_correction.py | `tests/evidence/scripts/a6_a7_okx_correction.py` | no-date |
| a9_asset_start_dates.py | `tests/evidence/scripts/a9_asset_start_dates.py` | no-date |
| a9_bitstamp_full.py | `tests/evidence/scripts/a9_bitstamp_full.py` | no-date |
| a9_coinbase_full.py | `tests/evidence/scripts/a9_coinbase_full.py` | no-date |
| a9_okx_only.py | `tests/evidence/scripts/a9_okx_only.py` | no-date |
| a9_okx_usdc_retry.py | `tests/evidence/scripts/a9_okx_usdc_retry.py` | no-date |
| a9_okx_v3.py | `tests/evidence/scripts/a9_okx_v3.py` | no-date |
| asset_master_builder.py | `tests/evidence/scripts/asset_master_builder.py` | no-date |
| audit_2026-11-11.py | `tests/evidence/scripts/audit_2026-11-11.py` | 2026-11-11 |
| check_7_no_data_supply.py | `tests/evidence/scripts/check_7_no_data_supply.py` | no-date |
| clean_legacy_registry.py | `tests/evidence/scripts/clean_legacy_registry.py` | no-date |
| cmc_top150_fetch.py | `tests/evidence/scripts/cmc_top150_fetch.py` | no-date |
| create_item_registry.py | `tests/evidence/scripts/create_item_registry.py` | no-date |
| final_clean_registry.py | `tests/evidence/scripts/final_clean_registry.py` | no-date |
| fix_tmap_caveats.py | `tests/evidence/scripts/fix_tmap_caveats.py` | no-date |
| fix_tmap_caveats_v2.py | `tests/evidence/scripts/fix_tmap_caveats_v2.py` | no-date |
| force_park_treasures.py | `tests/evidence/scripts/force_park_treasures.py` | no-date |
| generate_appendices.py | `tests/evidence/scripts/generate_appendices.py` | no-date |
| migrate_archive_content.py | `tests/evidence/scripts/migrate_archive_content.py` | no-date |
| park_legacy_treasures.py | `tests/evidence/scripts/park_legacy_treasures.py` | no-date |
| patch_v34_3fix.py | `tests/evidence/scripts/patch_v34_3fix.py` | no-date |
| patch_v34_7fixes.py | `tests/evidence/scripts/patch_v34_7fixes.py` | no-date |
| patch_v34_final.py | `tests/evidence/scripts/patch_v34_final.py` | no-date |
| patch_v34_final_2.py | `tests/evidence/scripts/patch_v34_final_2.py` | no-date |
| patch_v34_full.py | `tests/evidence/scripts/patch_v34_full.py` | no-date |
| patch_v34_session2.py | `tests/evidence/scripts/patch_v34_session2.py` | no-date |
| pol_bybit_test.py | `tests/evidence/scripts/pol_bybit_test.py` | no-date |
| r07_patch_item12.py | `tests/evidence/scripts/r07_patch_item12.py` | no-date |
| remove_junk_exchanges.py | `tests/evidence/scripts/remove_junk_exchanges.py` | no-date |
| update_tmap_bitstamp.py | `tests/evidence/scripts/update_tmap_bitstamp.py` | no-date |
| update_tmap_coinbase.py | `tests/evidence/scripts/update_tmap_coinbase.py` | no-date |
| validate_tmap.py | `tests/evidence/scripts/validate_tmap.py` | no-date |
| verify_test_map.sh | `tests/evidence/scripts/verify_test_map.sh` | no-date |
| test_map_audit_2026-11-13.txt | `tests/evidence/test_map_audit_2026-11-13.txt` | 2026-11-13 |

**جمع T4: 90**

## §5 — PENDING (نداریم، ولی لازم است)

| Test | Items | P | Why |
|---|---|---|---|
| Bitstamp candle cap | 01,09 | P0 | rate DONE، candle cap نه |
| Coinbase REST rate | 09 | P0 | GAP — هیچ‌جا نیست |
| C-019b (5-conn WS) | 09,11 | P0 | R-03 تصویب، تست نشده |
| WS Binance/Bybit | 11 | P1 | Part 2 v1.5 PROVISIONAL |
| A2 TF test (no_commit) | 06 | P1 | فایل شاهد ندارد — نیازمند بازنویسی TD (R-12b) |
| A2.5a OKX 1d=2017-10-10 | 06 | P1 | no_commit — همان A2 |
| USD1 DefiLlama | 15 | P3 | یک استیبل‌کوین |

**جمع PENDING: 7**

## §6 — Cross-Check

- اسکن: 135
- T1=20 T2=17 T3=8 T4=90
- جمع: 135
- ✅ Cross-check PASS

## §7 — پوشش ۳۰ آیتم

| Item | T1+T2 | PENDING |
|---|---|---|
| Item_01 | 10 | 1 |
| Item_02 | 0 | 0 |
| Item_03 | 12 | 0 |
| Item_04 | 5 | 0 |
| Item_05 | 3 | 0 |
| Item_06 | 0 | 2 |
| Item_07 | 1 | 0 |
| Item_08 | 1 | 0 |
| Item_09 | 11 | 3 |
| Item_10 | 1 | 0 |
| Item_11 | 5 | 2 |
| Item_12 | 1 | 0 |
| Item_13 | 1 | 0 |
| Item_14 | 0 | 0 |
| Item_15 | 5 | 1 |
| Item_16 | 2 | 0 |
| Item_17 | 0 | 0 |
| Item_18 | 1 | 0 |
| Item_19 | 0 | 0 |
| Item_20 | 0 | 0 |
| Item_21 | 0 | 0 |
| Item_22 | 0 | 0 |
| Item_23 | 0 | 0 |
| Item_24 | 0 | 0 |
| Item_25 | 0 | 0 |
| Item_26 | 0 | 0 |
| Item_27 | 0 | 0 |
| Item_28 | 0 | 0 |
| Item_29 | 0 | 0 |
| Item_30 | 0 | 0 |
