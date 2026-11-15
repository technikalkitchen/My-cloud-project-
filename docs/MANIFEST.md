# MANIFEST.md — Approved Tests Registry (v2)

**Generated:** 2026-11-15T20:40:53Z
**Approved tests:** 2 | **Errors:** 0
**Items with tests:** 1/30

## Workflow

1. تست جدید → از `TEMPLATE_test.py` کپی → JSON + Script → commit
2. Owner تأیید → یک خط به `tests/evidence/approved_tests.tsv`
3. `python3 tests/evidence/gen_manifest.py`

**JSON باید ۷ فیلد داشته باشد:** `test_name`, `item_ref`, `description`, `key_numbers`, `executed_at`, `script_path`, `data`

**Template:** `tests/evidence/TEMPLATE_test.py`

---

## Item Coverage

| Item | Name | Tests |
|---|---|---|
| 01 | Exchanges | ⬜ 0 |
| 02 | Aggregators | ⬜ 0 |
| 03 | Universe | ✅ 2 |
| 04 | Migration Map | ⬜ 0 |
| 05 | Canonical Pairs | ⬜ 0 |
| 06 | Timeframes | ⬜ 0 |
| 07 | Precision & Time | ⬜ 0 |
| 08 | Data Contract | ⬜ 0 |
| 09 | Rate Limit | ⬜ 0 |
| 10 | Error | ⬜ 0 |
| 11 | Cache | ⬜ 0 |
| 12 | Storage | ⬜ 0 |
| 13 | Bootstrap | ⬜ 0 |
| 14 | Incremental | ⬜ 0 |
| 15 | Supply | ⬜ 0 |
| 16 | OHLCV | ⬜ 0 |
| 17 | Exchange Volume | ⬜ 0 |
| 18 | Exchange Price | ⬜ 0 |
| 19 | Exchange MC | ⬜ 0 |
| 20 | Exchange Reliability | ⬜ 0 |
| 21 | Data Reliability | ⬜ 0 |
| 22 | Exchange Dominance | ⬜ 0 |
| 23 | Kitchen Price | ⬜ 0 |
| 24 | Kitchen Volume | ⬜ 0 |
| 25 | Kitchen MC | ⬜ 0 |
| 26 | Kitchen Coverage | ⬜ 0 |
| 27 | Ranking | ⬜ 0 |
| 28 | Grouping | ⬜ 0 |
| 29 | Kitchen Dominance | ⬜ 0 |
| 30 | Snapshot | ⬜ 0 |

---

## Item_01 — Exchanges

_هیچ تستی تأیید نشده_

## Item_02 — Aggregators

_هیچ تستی تأیید نشده_

## Item_03 — Universe

| File | Date | Description | Key Numbers |
|---|---|---|---|
| cmc_classify_2026-11-15.json | 2026-11-15 | Classification of 125 universe assets based on CMC tags | total_count=125 | stablecoin_count=13 | regular_count=112 | wrapped_count=0 | support_count=1 |
| cmc_top125_fetch_2026-11-15.json | 2026-11-15 | Universe selection: top 125 from CMC 150 (excludes 25 lowest ranks) | universe_count=125 | excluded_count=25 | stablecoin_count=13 | wrapped_count=0 | highest_rank_included=1 | lowest_rank_included=125 |

## Item_04 — Migration Map

_هیچ تستی تأیید نشده_

## Item_05 — Canonical Pairs

_هیچ تستی تأیید نشده_

## Item_06 — Timeframes

_هیچ تستی تأیید نشده_

## Item_07 — Precision & Time

_هیچ تستی تأیید نشده_

## Item_08 — Data Contract

_هیچ تستی تأیید نشده_

## Item_09 — Rate Limit

_هیچ تستی تأیید نشده_

## Item_10 — Error

_هیچ تستی تأیید نشده_

## Item_11 — Cache

_هیچ تستی تأیید نشده_

## Item_12 — Storage

_هیچ تستی تأیید نشده_

## Item_13 — Bootstrap

_هیچ تستی تأیید نشده_

## Item_14 — Incremental

_هیچ تستی تأیید نشده_

## Item_15 — Supply

_هیچ تستی تأیید نشده_

## Item_16 — OHLCV

_هیچ تستی تأیید نشده_

## Item_17 — Exchange Volume

_هیچ تستی تأیید نشده_

## Item_18 — Exchange Price

_هیچ تستی تأیید نشده_

## Item_19 — Exchange MC

_هیچ تستی تأیید نشده_

## Item_20 — Exchange Reliability

_هیچ تستی تأیید نشده_

## Item_21 — Data Reliability

_هیچ تستی تأیید نشده_

## Item_22 — Exchange Dominance

_هیچ تستی تأیید نشده_

## Item_23 — Kitchen Price

_هیچ تستی تأیید نشده_

## Item_24 — Kitchen Volume

_هیچ تستی تأیید نشده_

## Item_25 — Kitchen MC

_هیچ تستی تأیید نشده_

## Item_26 — Kitchen Coverage

_هیچ تستی تأیید نشده_

## Item_27 — Ranking

_هیچ تستی تأیید نشده_

## Item_28 — Grouping

_هیچ تستی تأیید نشده_

## Item_29 — Kitchen Dominance

_هیچ تستی تأیید نشده_

## Item_30 — Snapshot

_هیچ تستی تأیید نشده_

---

## PENDING Tests

_هیچ تست PENDING ثبت نشده_
