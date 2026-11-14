# MANIFEST.md - Self-Sufficient Test Registry

**Generated:** 2026-11-14T15:24:43Z
**Total files:** 130 | **PENDING:** 5

**Regenerate:** `bash tests/evidence/scan_repo.sh && python3 tests/evidence/gen_manifest.py`
**Manual edits:** `triage.tsv` (tier/items) + `pending.tsv`

## §0 — Version Rule

| Status | File |
|---|---|
| Valid (tests) | MANIFEST.md (this file) |
| Knowledge (R-Laws) | docs/B_items/Cross_Item_Notes.md |
| Scope | docs/MAP.md |
| Item-Centric view | docs/TEST_MAP_v4.md |
| Archive | v3.4_FINAL · *.bak |


## §1 — T1-Core: In TEST_MAP (شاهد قطعی) (18)

| File | Item | Date | Description | Key Numbers |
|---|---|---|---|---|
| 2026-11-07_A4_OHLCV_Format.md | 07,08,10,16 | 2026-11-07 | 5 ناسازگاری OHLCV (field order، 4 ts format، float، direction، count) | - |
| 2026-11-07_migration_extract.md | 04 | 2026-11-07 | migration extract text | - |
| 7_no_data_resolved_2026-11-11.json | 03,15 | 2026-11-11 | 7 NO_DATA RESOLVED — all new assets no 2017 data | resolution_date=2026-11-11 | issue=Symbol Collision caused by incorrect CMC... | resolved_assets{7} | conclusion=All 7 are new assets. CMC historical API... |
| A6_A7_discovery_2026-11-08.json | 03,04 | 2026-11-08 | 3 migration + 3 delisted + KMNO | migrations[3] | delisted[3] | survivors[1] | cmc_id_changes[1] |
| A6_A7_okx_correction_2026-11-09.json | 04 | 2026-11-09 | POL=2024-09-03 RENDER=2024-07-14 S=2025-01-20 (CONFIRMED) | corrected_at=2026-11-08T21:36:15.298249+00:00 | reason=OKX walk-back correction for A6_A7 bug (... | source_discovery_file=tests/evidence/A6_A7_discovery_2026-11-0... | assets{6} |
| a9_asset_start_dates_2026-11-08.json | 01,03,04,18 | 2026-11-08 | +04 (migration), +18 (price start) | BTC{4} | ETH{4} | USDT{4} | BNB{4} | XRP{4} | USDC{4} |
| a9_bitstamp_2026-11-11.json | 01 | 2026-11-11 | 85/150 TESTED (full run) | generated_at=2026-11-11T15:02:04.984386+00:00 | assets{150} |
| a9_coinbase_2026-11-11.json | 01,03,05 | 2026-11-11 | 99/150 usdt_usd_start=2021-05-04 22 Direct + 77 Converted | generated_at=2026-11-11T14:24:41.096389+00:00 | usdt_usd_start=2021-05-04 | assets{150} |
| a9_okx_2026-11-09.json | 01,03 | 2026-11-09 | 105/150 TESTED USDT+USD+USDC | BTC{3} | ETH{3} | USDT{3} | BNB{3} | XRP{3} | USDC{3} |
| a9_okx_usdc_retry_2026-11-09.json | 01 | 2026-11-09 | 106/150 (+EURC) 600-day partial | XMR{3} | USDe{3} | DAI{3} | XAUt{3} | QNT{3} | M{3} |
| a9_okx_v3_2026-11-09.json | 05,18 | 2026-11-09 | BTC-pair PENDING USD PENDING USDT 105/150 | generated_at=2026-11-09T14:03:23.296574+00:00 | source_v1=tests/evidence/a9_okx_2026-11-09.json | assets{150} | summary{4} |
| asset_universe_master_2026-11-08.json | 03 | 2026-11-08 | 195 union | total_unique_assets=195 | by_reason_counts{6} | assets{195} |
| audit_2026-11-11.json | all | 2026-11-11 | 7 open questions answered — commit 8998ecf | generated_at=2026-11-10T16:14:13Z | section_a_repo{10} | section_b_cmc{7} |
| cmc_top150_2026-11-08.json | 03 | 2026-11-08 | 150 CMC authoritative | fetched_at=2026-11-08T16:23:45.155887+00:00 | count=150 | assets[150] |
| final_125_supply.json | 03,15 | no-date | 118 tag FILLED | - |
| final_125_supply.json#2 | 03,15 | no-date | 118 tag FILLED | - |
| pol_bybit_test_2026-11-08.json | 04 | 2026-11-08 | same_asset close diff 0.14% launchTime=null test_date=2023-10-25 | instruments_info{5} | pol_price{3} | matic_price{3} | interpretation=same_asset | test_date=2023-10-25 00:00 | test_ts=1698192000000 |
| supply_timeseries_2026-11-07.json | 12,15 | 2026-11-07 | 117 keys 13.17MB | BTC[3597] | ETH[3597] | USDT[3597] | BNB[3232] | XRP[3597] | USDC[2867] |

## §3 — T1-Driver Scripts (تولیدکننده شواهد) (15)

| File | Item | Date | Description | Key Numbers |
|---|---|---|---|---|
| a6_a7_discovery.py | 03,04 | no-date | produces A6_A7_discovery.json | - |
| a6_a7_okx_correction.py | 04 | no-date | produces A6_A7_okx_correction.json | - |
| a9_asset_start_dates.py | 01,03,04,18 | no-date | produces a9_asset_start_dates.json | - |
| a9_bitstamp_full.py | 01 | no-date | produces a9_bitstamp_11.json | - |
| a9_coinbase_full.py | 01,03,05 | no-date | produces a9_coinbase_11.json | - |
| a9_okx_only.py | 01,03 | no-date | produces a9_okx_2026-11-09.json | - |
| a9_okx_usdc_retry.py | 01 | no-date | produces a9_okx_usdc_retry.json | - |
| a9_okx_v3.py | 05,18 | no-date | produces a9_okx_v3.json | - |
| asset_master_builder.py | 03 | no-date | produces asset_universe_master.json | - |
| audit_2026-11-11.py | all | 2026-11-11 | produces audit_2026-11-11.json | - |
| bitstamp_diagnostic.py | 01 | no-date | script (was T1-core) | - |
| check_7_no_data_supply.py | 03,15 | no-date | produces 7_no_data_resolved.json | - |
| cmc_top150_fetch.py | 03 | no-date | produces cmc_top150.json | - |
| coinbase_btc_diagnostic.py | 01,05 | no-date | script (was T1-core) | - |
| pol_bybit_test.py | 04 | no-date | produces pol_bybit_test.json | - |

## §3b — T2: Active with Reconfirm (rate_limit ۲۹-۳۰ Oct) (17)

| File | Date | Description | Key Numbers |
|---|---|---|---|
| 2026-10-29_binance_klines_weight.txt | 2026-10-29 | weight=2 reset at minute boundary | - |
| 2026-10-29_binance_limit1000.txt | 2026-10-29 | Binance cap 1000 | - |
| 2026-10-29_binance_sol.txt | 2026-10-29 | Binance SOL cap | - |
| 2026-10-29_header_check.txt | 2026-10-29 | only Binance returns RL header | - |
| 2026-10-29_okx_safe.txt | 2026-10-29 | OKX safe | - |
| 2026-10-30_bitstamp_coinbase_cryptocom_safe.txt | 2026-10-30 | safe response | - |
| 2026-10-30_coinbase_websocket_all.txt | 2026-10-30 | 103 pairs 9659 msg/60s | - |
| 2026-10-30_okx_history_http.txt | 2026-10-30 | 2 req/s effective | - |
| 2026-10-30_okx_websocket_all.txt | 2026-10-30 | 89 pairs 1385 msg/60s confirm=0 | - |
| 2026-10-30_okx_websocket_test.txt | 2026-10-30 | OKX WS v1 | - |
| 2026-10-30_okx_websocket_test_v2.txt | 2026-10-30 | BTC 34 ETH 27 SOL 21 | - |
| A6_A7_discovery_2026-11-08_summary.md | 2026-11-08 | summary | - |
| a9_asset_start_dates_2026-11-08_summary.md | 2026-11-08 | summary | - |
| audit_2026-11-11.md | 2026-11-11 | summary mirror | - |
| cmc_internal_extended.yml | no-date | CMC extended workflow | - |
| final_supply_harvest.yml | no-date | data_source workflow (118 records) | - |
| test003_manual.yml | no-date | test003 workflow | - |

## §4 — T4 Helper Scripts (23)

| File | Date | Description | Key Numbers |
|---|---|---|---|
| __init__.py | no-date | not a test - helper | - |
| adapters.py | no-date | not a test - helper | - |
| config.py | no-date | not a test - helper | - |
| create_item_registry.py | no-date | not a test - helper | - |
| final_clean_registry.py | no-date | not a test - helper | - |
| fix_tmap_caveats.py | no-date | not a test - helper | - |
| fix_tmap_caveats_v2.py | no-date | not a test - helper | - |
| force_park_treasures.py | no-date | not a test - helper | - |
| generate_appendices.py | no-date | not a test - helper | - |
| migrate_archive_content.py | no-date | not a test - helper | - |
| park_legacy_treasures.py | no-date | not a test - helper | - |
| patch_v34_3fix.py | no-date | not a test - helper | - |
| patch_v34_7fixes.py | no-date | not a test - helper | - |
| patch_v34_final.py | no-date | not a test - helper | - |
| patch_v34_final_2.py | no-date | not a test - helper | - |
| patch_v34_full.py | no-date | not a test - helper | - |
| patch_v34_session2.py | no-date | not a test - helper | - |
| r07_patch_item12.py | no-date | not a test - helper | - |
| remove_junk_exchanges.py | no-date | not a test - helper | - |
| runner.py | no-date | not a test - helper | - |
| update_tmap_bitstamp.py | no-date | not a test - helper | - |
| update_tmap_coinbase.py | no-date | not a test - helper | - |
| validate_tmap.py | no-date | not a test - helper | - |

## §5 — T4 Obsolete Workflows (15)

| File | Date | Description | Key Numbers |
|---|---|---|---|
| cmc_aggressive_fill.yml | no-date | not a test - obsolete | - |
| cmc_earliest_dates.yml | no-date | not a test - obsolete | - |
| cmc_fill_40.yml | no-date | not a test - obsolete | - |
| combined_supply_tests.yml | no-date | not a test - obsolete | - |
| fill_gaps.yml | no-date | not a test - obsolete | - |
| test001_manual.yml | no-date | not a test - obsolete | - |
| test_actions.yml | no-date | not a test - obsolete | - |
| test_comprehensive_data.yml | no-date | not a test - obsolete | - |
| test_cron_timing.yml | no-date | not a test - obsolete | - |
| test_crypto2.yml | no-date | not a test - obsolete | - |
| test_crypto2_v2.yml | no-date | not a test - obsolete | - |
| test_external_api.yml | no-date | not a test - obsolete | - |
| test_historical_supply.yml | no-date | not a test - obsolete | - |
| verify_and_fill.yml | no-date | not a test - obsolete | - |
| verify_top125_supply.yml | no-date | not a test - obsolete | - |

## §6 — T4 Test Outputs (35)

| File | Date | Description | Key Numbers |
|---|---|---|---|
| aggressive_fill_29.json | no-date | not a test - output | - |
| cmc_fill_40.json | no-date | not a test - output | - |
| cmc_ids.json | no-date | not a test - output | - |
| coingecko_retry.json | no-date | not a test - output | - |
| earliest_dates.json | no-date | not a test - output | - |
| fill_gaps_results.json | no-date | not a test - output | - |
| latest_run.log | no-date | not a test - output | - |
| latest_run.log#10 | no-date | not a test - output | - |
| latest_run.log#11 | no-date | not a test - output | - |
| latest_run.log#12 | no-date | not a test - output | - |
| latest_run.log#13 | no-date | not a test - output | - |
| latest_run.log#14 | no-date | not a test - output | - |
| latest_run.log#15 | no-date | not a test - output | - |
| latest_run.log#16 | no-date | not a test - output | - |
| latest_run.log#17 | no-date | not a test - output | - |
| latest_run.log#18 | no-date | not a test - output | - |
| latest_run.log#2 | no-date | not a test - output | - |
| latest_run.log#3 | no-date | not a test - output | - |
| latest_run.log#4 | no-date | not a test - output | - |
| latest_run.log#5 | no-date | not a test - output | - |
| latest_run.log#6 | no-date | not a test - output | - |
| latest_run.log#7 | no-date | not a test - output | - |
| latest_run.log#8 | no-date | not a test - output | - |
| latest_run.log#9 | no-date | not a test - output | - |
| results.json | no-date | not a test - output | - |
| results.json#2 | no-date | not a test - output | - |
| results.json#3 | no-date | not a test - output | - |
| results.json#4 | no-date | not a test - output | - |
| results.json#5 | no-date | not a test - output | - |
| summary.txt | no-date | not a test - output | - |
| supply_timeseries_2026-11-07_errors.json | 2026-11-07 | not a test - output | - |
| top125.json | no-date | not a test - output | - |
| top125_mapped.json | no-date | not a test - output | - |
| verification_results.json | no-date | not a test - output | - |
| verify_125.json | no-date | not a test - output | - |

## §8 — T3 Amateur Period (7)

| File | Date | Description | Key Numbers |
|---|---|---|---|
| 2026-10-27_requirements.txt | 2026-10-27 | requests | - |
| 2026-10-27_summary.txt | 2026-10-27 | ===== results/test001_manual/run_39050926831/test001-results/results.json ===== | - |
| 2026-10-28_5m_since_2017.tsv | 2026-10-28 | historical — superseded by A2 (7 Nov) | - |
| 2026-10-28_coverage_matrix.tsv | 2026-10-28 | historical — superseded by A9 composite | - |
| 2026-10-28_okx_cc_test.txt | 2026-10-28 | === Sanity: OKX reachable? === | - |
| 2026-10-28_test_real_check.txt | 2026-10-28 | === 1. Binance BTCUSDT 5m — از 2017-08-17؟ === | - |
| 2026-10-30_1h_1d_coverage.txt | 2026-10-30 | historical — superseded by A2.5a | - |

## §9 — Real Uncategorized (0)

_هیچ فایلی بدون طبقه‌بندی نیست_ ✅

## §10 — PENDING Tests (5)

| Test | Item | P | Why |
|---|---|---|---|
| Bitstamp candle cap | 01,09 | P0 | سقف 300 تأیید نشده |
| Coinbase REST rate | 09 | P0 | GAP — هرگز تست نشد |
| C-019b (5-conn WS) | 09,11 | P0 | R-03 تصویب، تست نشده |
| WS Binance/Bybit | 11 | P1 | Part 2 v1.5 PROVISIONAL |
| USD1 DefiLlama | 15 | P3 | کم‌اولویت |
