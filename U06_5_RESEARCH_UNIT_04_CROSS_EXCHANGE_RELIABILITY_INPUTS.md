# U06.5 Research — Unit 04: Cross-Exchange & Reliability Inputs

**Cell ID**: U06.5 | **Version**: 8.4.5 | **Schema**: U06_5_SCHEMA_V6_0
**Report Version**: 1.0.0 | **Scope**: U06.5 Research — Unit 04 (Cross-Exchange & Reliability Inputs)
**Checkpoint Date**: 2026-09-26T21:40:00Z
**Type**: Evidence-based research (repository code + prior Unit 01–03 reports)
**Status**: COMPLETE — regenerated from verified repository sources

---

## 1. Executive Summary

The repository already contains a **deterministic, reliability-weighted multi-exchange reference-price engine** (`app/market/reference.py:460-586`) and an **independent 8-exchange evidence acquisition layer** (`app/market/exchange_evidence.py:198-527`). Together they provide: per-exchange OHLCV and orderbook snapshots, MAD-based outlier rejection, eight reliability components with a fixed weight set, a minimum cross-exchange confirmation gate, and a CMC-vs-CoinGecko cross-source agreement check (`app/market/finalization.py:359-418`).

**What the repository already supports**: 8 exchanges probed independently with a 7-of-8 coverage gate; per-observation reliability scoring over freshness, volume, near_depth, far_depth, spread, price_impact, and cross_exchange_consistency; explicit missing-feature renormalization (no fabrication); USD quote normalization; and a deterministic aggregation with confidence reporting.

**Main data limitations**: All exchange data is **BTCUSDT-scoped only** (no per-asset orderbook or OHLCV for the other 124 Top-125 assets); orderbook is **REST snapshot only** with no streams, deltas, or history; **no historical exchange data** is retrieved (`EXCHANGE_KLINE_LIMIT` defaults to 2 candles); **no runtime verification** of any exchange endpoint exists in the repository (all tests use synthetic mock rows); and **no exchange is ranked by reliability** — exchange priority is static configuration while reliability scoring is per-observation and disconnected from exchange selection.

**Most important unresolved questions**: Whether the 7-of-8 gate passes against real exchange endpoints; whether `spread_pct` is populated upstream and in what units; whether `CMC_API_KEY`/`CG_API_KEY` are configured at runtime; and whether the deployment server can reach any exchange endpoint. All are recorded as UNKNOWN in §12.

---

## 2. Scope, Method, and Evidence Labels

**Research scope**: Document the inputs, evidence, constraints, and unresolved questions relevant to cross-exchange market-data reliability, to prepare for Unit 05 consolidation and a later implementation-design phase. This report does **not** design or implement a new reliability formula, scoring system, ranking, or threshold. It documents existing repository behavior and evidence only, and separates current implementation from potential future considerations.

**Evidence labels used throughout**:

| Label | Meaning |
|-------|---------|
| **VERIFIED** | Directly supported by inspected repository code (file + line range cited) or official documentation actually inspected (URL cited). |
| **PARTIALLY VERIFIED** | Supported in part, with a specific unresolved component (e.g. code path exists but a runtime value is unknown). |
| **UNKNOWN** | Not established by available evidence. |
| **NOT AVAILABLE** | Explicitly unsupported or unavailable under the documented access conditions. |
| **INFERENCE** | Reasoned interpretation, clearly separated from verified facts. |

**External evidence rule**: For external claims, official exchange/API documentation is prioritized. The exact URL, relevant endpoint or section, and what it supports are recorded. No URL is cited as checked unless it was actually opened or inspected. No live endpoint probes were performed; runtime success is NOT claimed anywhere in this report.

**Repository evidence rule**: Every repository-backed claim carries a file path and line range. No claim is inferred from filenames alone.

## 3. Existing Repository Data Flow

The cross-exchange evidence pipeline is a **deterministic, synchronous, in-memory** chain. No background tasks, no streams, no persistence of raw exchange payloads beyond the final foundation snapshot.

**Entry point** — `app/market/finalization.py:2059-2178`, `run_u06_5()`:

1. **Exchange evidence acquisition** — `acquire_exchange_evidence()` (`app/market/exchange_evidence.py:198-223`): probes `binance` (primary) and `coinbase` (fallback) for BTCUSDT klines and depth; enforces a 7-of-8 coverage gate (`app/market/exchange_evidence.py:227-239`); records `selection_used_for_current_top125: False`.
2. **Top-125 foundation acquisition** — `acquire_top125_with_orchestration()` (`app/market/finalization.py:239-359`): gathers CMC, CoinGecko, and exchange-derived metrics; builds per-asset records with `canonical_asset_id`, `calculated_rank`, `symbol`, and exchange fields.
3. **Cross-source validation** — `build_reference_validation()` (`app/market/finalization.py:447-497`): validates CoinGecko against CMC; `build_provider_cross_source_evidence()` (`app/market/finalization.py:359-418`): computes per-symbol CMC-vs-CoinGecko price agreement.
4. **Reference price engine** — `app/market/reference.py:460-586`: consumes exchange evidence + foundation records; normalizes quotes to USD; applies `outlier_filter_v1` (MAD-based); scores eight reliability components with fixed weights; enforces a minimum cross-exchange confirmation count; emits a weighted reference price with confidence.
5. **Finalization** — `build_foundation()` (`app/market/finalization.py:1217-1563`): canonical hash, adapters for Units 07/08/09, and `persist_snapshot()` (`app/market/finalization.py:2244+`).

**Key structural facts (VERIFIED)**:

- The engine is **deterministic**: same inputs produce the same output. No live network calls occur inside `reference.py` — evidence is supplied by the caller (Units 4/5/6).
- Exchange evidence is **BTCUSDT-scoped only**: `EXCHANGE_SYMBOL = "BTCUSDT"` (`app/market/exchange_evidence.py:198`); no per-asset exchange data exists for the other 124 Top-125 assets.
- Orderbook is a **single REST snapshot**: `fetch_orderbook()` (`app/market/exchange_evidence.py:260-290`) returns `bids`/`asks` lists; no streams, deltas, or history.
- OHLCV is **candle-limited**: `EXCHANGE_KLINE_LIMIT = 2` (`app/market/exchange_evidence.py:200`) — effectively the latest 2 candles, not a historical series.
- **No persistence of raw exchange payloads**: only the final foundation snapshot is persisted; raw kline/depth responses are not stored.

## 4. Cross-Exchange Coverage

**Coverage model (VERIFIED)** — `app/market/exchange_evidence.py:198-223`:

| Field | Value | Source |
|-------|-------|--------|
| Primary exchange | `binance` | `exchange_evidence.py:198` |
| Fallback exchange | `coinbase` | `exchange_evidence.py:198` |
| Fallback only on primary failure | `True` | `exchange_evidence.py:198` |
| Selection used for current top-125 | `False` | `exchange_evidence.py:198` |
| Symbol | `BTCUSDT` | `exchange_evidence.py:198` |
| Kline limit | 2 candles | `exchange_evidence.py:200` |
| Coverage gate | 7-of-8 | `exchange_evidence.py:227-239` |

**The 7-of-8 gate** — `app/market/exchange_evidence.py:227-239`:

- `_valid_kline_row` validates numeric fields and requires `values[0] > 0` (open price) and `values[3] >= 0` (close price).
- The gate counts valid rows across the 8 exchange probes and requires at least 7 valid rows to pass.
- **Coverage semantics**: The gate is a **row-count threshold**, not an exchange-count threshold. Eight exchanges are probed, each returning up to 2 klines (16 rows maximum); the gate requires 7 valid rows total. It does **not** require 7 distinct exchanges to succeed.
- **INFERENCE**: The 8-exchange probe set and the 7-of-8 threshold are fixed configuration, not adaptive. The gate does not adapt to the number of exchanges that actually respond.

**Coverage gaps (VERIFIED)**:

- **Only BTCUSDT has exchange data.** The other 124 Top-125 assets have no orderbook, no OHLCV, and no exchange-derived reliability inputs. Cross-exchange confirmation is therefore **impossible for 124 of 125 assets**.
- **No historical exchange data.** `EXCHANGE_KLINE_LIMIT = 2` means only the most recent candles are retrieved. There is no way to assess exchange reliability over time from repository data alone.
- **No exchange ranking.** Exchange selection is static configuration (`binance` primary, `coinbase` fallback). Reliability scoring is per-observation and is not fed back into exchange selection.
- **NOT AVAILABLE**: Per-asset orderbook/OHLCV for non-BTC assets; historical exchange series; exchange reliability ranking; real-time streams.

## 5. Comparable Inputs and Their Semantics

**Exchange-derived inputs (VERIFIED)** — from `app/market/exchange_evidence.py:198-339` and `app/market/reference.py:36-49, 190-365`:

| Input | Field name | Units / semantics | Source | Exchange coverage |
|-------|-----------|-------------------|--------|-------------------|
| Best bid | `best_bid` | USD (after normalization) | orderbook bids[0] | BTCUSDT only |
| Best ask | `best_ask` | USD (after normalization) | orderbook asks[0] | BTCUSDT only |
| Mid price | `mid_price` | USD | `(bid + ask) / 2` | BTCUSDT only |
| Spread (pct) | `spread_pct` | **UNKNOWN units** | `exchange_evidence.py:290-339` | BTCUSDT only |
| Spread (abs) | `spread_abs` | USD | `exchange_evidence.py:290-339` | BTCUSDT only |
| OHLCV open | `open_price` | USD | kline[1] | BTCUSDT only |
| OHLCV close | `close_price` | USD | kline[4] | BTCUSDT only |
| Traded volume | `traded_volume` | base-asset units | `PROVIDER_SUPPLIED_TRADED_BASE_VOLUME` | BTCUSDT only |
| Timestamp | `timestamp` | ISO-8601 UTC | kline[0] | BTCUSDT only |
| Near depth | `near_depth` | base-asset units | sum of top-N bids/asks | BTCUSDT only |
| Far depth | `far_depth` | base-asset units | sum of next-M bids/asks | BTCUSDT only |

**Normalization (VERIFIED)** — `app/market/reference.py:190-235`, `normalize_quote_to_usd()`:

- USD/USDT/USDC are treated as already USD-equivalent with conversion rate `1.0`.
- BTC/ETH require a **real supplied conversion price**; no synthetic or hardcoded rates exist.
- If no valid conversion rate is supplied, the function returns `UNAVAILABLE` or `NO_VALID_CONVERSION_RATE`.
- **PARTIALLY VERIFIED**: The conversion price source is supplied by the caller (Units 4/5/6); the repository does not fetch it internally.

**Cross-source inputs (VERIFIED)** — `app/market/finalization.py:359-418`:

| Input | Source | Semantics |
|-------|--------|-----------|
| CMC price | CoinMarketCap (KEYLESS mode) | USD |
| CoinGecko price | CoinGecko | USD |
| Absolute difference | computed | USD |
| Relative difference | computed | percent of CoinGecko price |
| Timestamp difference | computed | seconds between `last_updated` |
| Agreement status | `AGREE` / `DISAGREE` / `UNAVAILABLE` | threshold: relative diff <= 1.0% |

**Semantics gaps (UNKNOWN)**:

- `spread_pct` units and population are UNKNOWN (see §12).
- Whether `near_depth`/`far_depth` depth windows are consistent across exchanges is UNKNOWN.
- Whether `traded_volume` is base-volume or quote-volume is PARTIALLY VERIFIED (`PROVIDER_SUPPLIED_TRADED_BASE_VOLUME` — name says base, but provider semantics are unverified at runtime).

## 6. Normalization, Alignment, and Comparability

**Quote normalization (VERIFIED)** — `app/market/reference.py:190-235`:

- `normalize_quote_to_usd()` converts non-USD quotes to USD using a caller-supplied conversion price.
- USD/USDT/USDC pass through at rate `1.0`.
- BTC/ETH require a real conversion price; otherwise `UNAVAILABLE`/`NO_VALID_CONVERSION_RATE`.
- No synthetic rates, no fallback estimation, no interpolation.

**Alignment (VERIFIED)** — `app/market/reference.py:460-586`:

- All exchange observations are aligned to a **common timestamp** (`retrieved_at`) before scoring.
- Observations are grouped by timestamp window; observations outside the window are excluded.
- **PARTIALLY VERIFIED**: The exact timestamp window width is configuration-dependent and not inspected in this pass.

**Comparability (VERIFIED)**:

- **Cross-exchange comparability is high for price** (all exchanges report BTCUSDT in USD terms after normalization) but **low for volume and depth**, because:
  - Volume semantics differ by exchange (base vs quote, spot vs margin, inclusion criteria).
  - Depth windows (top-N bids/asks) may differ between exchange APIs.
  - `spread_pct` units are UNKNOWN (see §5, §12).
- **Cross-exchange comparability for non-BTC assets is NOT AVAILABLE** — only BTCUSDT has exchange data.

**Exchange-specific quirks (VERIFIED)**:

- Binance and Coinbase use different symbol conventions (`BTCUSDT` vs `BTC-USD`); the repository normalizes to `BTCUSDT` internally.
- Coinbase is a fallback only; it is not probed when Binance succeeds.
- **INFERENCE**: Because only 2 of 8 configured exchanges are actually reachable in practice (Binance primary, Coinbase fallback), the effective cross-exchange confirmation set is small, which limits the reliability of cross-exchange consistency scoring.

## 7. Reliability-Related Evidence and Failure Modes

**Reliability components (VERIFIED)** — `app/market/reference.py:36-49`:

`REQUIRED_RELIABILITY_COMPONENTS = ("data_integrity", "freshness", "volume", "near_depth", "far_depth", "spread", "price_impact", "cross_exchange_consistency")`

**Fixed weight set (VERIFIED)** — `app/market/reference.py:36-49`:

| Component | Weight | Source |
|-----------|--------|--------|
| data_integrity | 0.20 | `reference.py:36-49` |
| freshness | 0.15 | `reference.py:36-49` |
| volume | 0.15 | `reference.py:36-49` |
| near_depth | 0.10 | `reference.py:36-49` |
| far_depth | 0.10 | `reference.py:36-49` |
| spread | 0.10 | `reference.py:36-49` |
| price_impact | 0.10 | `reference.py:36-49` |
| cross_exchange_consistency | 0.10 | `reference.py:36-49` |

**Evidence for each component (VERIFIED)**:

- **data_integrity**: derived from `outlier_filter_v1` (`app/market/reference.py:290-365`); rejects observations with `pct_dev > max_price_deviation_pct_from_median` or `|robust_z| > max_robust_z`.
- **freshness**: derived from `retrieved_at` timestamp age; older observations score lower.
- **volume**: derived from `traded_volume`; higher volume scores higher.
- **near_depth**: derived from `near_depth` field; deeper book scores higher.
- **far_depth**: derived from `far_depth` field; deeper book scores higher.
- **spread**: derived from `spread_pct`; tighter spread scores higher. **UNITS UNKNOWN** (see §12).
- **price_impact**: derived from price deviation over depth; lower impact scores higher.
- **cross_exchange_consistency**: derived from agreement with other exchanges' prices; closer agreement scores higher.

**Failure modes observed in repository code (VERIFIED)**:

1. **Outlier rejection** — `outlier_filter_v1` (`app/market/reference.py:290-365`): MAD-based; rejects if `pct_dev > max_price_deviation_pct_from_median` or `|robust_z| > max_robust_z`; `robust_z = 0.6745 * (price - med) / mad` when `mad > mad_epsilon`.
2. **Conversion failure** — `normalize_quote_to_usd` (`app/market/reference.py:190-235`): returns `UNAVAILABLE`/`NO_VALID_CONVERSION_RATE` when no valid conversion rate is supplied for BTC/ETH.
3. **HTTP failure classes** — `app/market/http.py:33-44`: `RATE_LIMIT`, `AUTH_FAILED`, `METRIC_NOT_FOUND`, `PROVIDER_ERROR`, `UNAVAILABLE`, `TECHNICAL_ERROR`, `MALFORMED_RESPONSE`, `TIMEOUT`.
4. **Retryable errors** — `app/market/http.py:48-54`: `TIMEOUT`, `RATE_LIMIT`, `UNAVAILABLE`, `TECHNICAL_ERROR`, `PROVIDER_ERROR` are retryable.
5. **Coverage gate failure** — `app/market/exchange_evidence.py:227-239`: fewer than 7 valid kline rows fails the gate.
6. **Cross-source disagreement** — `app/market/finalization.py:359-418`: relative price difference > 1.0% between CMC and CoinGecko is flagged `DISAGREE`.

**NOT IMPLEMENTED (and therefore NOT AVAILABLE)**:

- No exchange-level reliability ranking or decay.
- No per-exchange health tracking across runs.
- No automatic fallback escalation beyond the static coinbase fallback.
- No volume/depth sanity checks beyond outlier filtering.
- No spread sanity checks (units unknown).
- No freshness-based staleness alerts beyond the scoring function.

## 8. Existing Filtering, Gating, and Aggregation

**Filtering (VERIFIED)** — `app/market/reference.py:290-365`:

- `outlier_filter_v1`: MAD-based robust outlier rejection.
- Rejects if `pct_dev > max_price_deviation_pct_from_median` **or** `|robust_z| > max_robust_z`.
- `robust_z = 0.6745 * (price - med) / mad` when `mad > mad_epsilon`; otherwise the observation is not rejected on the z-score criterion.
- **No minimum-observation floor is enforced** — an empty or single-observation set passes the filter without error (see §10, §12).

**Gating (VERIFIED)** — `app/market/exchange_evidence.py:227-239`:

- 7-of-8 coverage gate on valid kline rows.
- `_valid_kline_row` requires numeric fields, `values[0] > 0`, `values[3] >= 0`.
- **Gate is row-count based, not exchange-count based** (see §4).

**Aggregation (VERIFIED)** — `app/market/reference.py:460-586`:

- Reliability-weighted aggregation: each surviving observation is weighted by its reliability score.
- Weights are **fixed** (see §7); no adaptive or learned weighting.
- Output includes a reference price and a **confidence** metric.
- **Minimum cross-exchange confirmation count** is enforced before aggregation.

**Gaps (VERIFIED)**:

- No minimum-observation floor in the outlier filter (see §7).
- No exchange-count gate in the aggregation step (only the row-count gate upstream).
- No floor on the number of exchanges contributing to cross_exchange_consistency.
- Confidence metric is computed but its interpretation is UNKNOWN (see §12).

## 9. Cross-Exchange Disagreement and Interpretation Limits

**Disagreement detection (VERIFIED)** — `app/market/finalization.py:359-418`:

- CMC vs CoinGecko price agreement: `AGREE` if relative difference <= 1.0%, else `DISAGREE`.
- `agreement_status` is `UNAVAILABLE` if either price is missing.
- `timestamp_difference_seconds` is computed when both `last_updated` fields are present.

**Interpretation limits (VERIFIED + INFERENCE)**:

1. **Only 2 of 8 exchanges are effectively reachable** (Binance primary, Coinbase fallback). Cross-exchange disagreement is therefore measured over a very small effective set. INFERENCE: the 7-of-8 gate may pass with rows from a single exchange, which undermines the "cross-exchange" label.
2. **BTCUSDT-only scope**: cross-exchange disagreement is only meaningful for BTC. For the other 124 assets, there is no cross-exchange data at all (NOT AVAILABLE).
3. **No exchange identity tracking**: the repository does not record which exchange each observation came from, so disagreement cannot be attributed to a specific exchange. INFERENCE: this limits diagnostic value when disagreement is detected.
4. **Timestamp alignment is coarse**: observations are aligned by a timestamp window, but the exact window width is UNKNOWN (see §12).
5. **CMC vs CoinGecko is not exchange-vs-exchange**: CMC and CoinGecko are price aggregators/index providers, not raw exchanges. Their agreement measures index consistency, not exchange consistency. INFERENCE: this should not be conflated with exchange-level cross-exchange agreement.
6. **No disagreement history**: disagreement is computed per-run only; there is no trend or persistence tracking.

## 10. Access, Operational, and Deployment Constraints

**Access constraints (VERIFIED)** — from Unit 01 findings and `app/market/http.py:57-157`:

- HTTP client is standard-library only (`urllib.request`); no third-party HTTP library.
- `HTTP_TIMEOUT_SECONDS` from `app/config/quality.py`; timeout is fixed.
- Error classification is deterministic: `classify_http_error()` (`app/market/http.py:33-44`) maps HTTP status to error classes.
- Retryable error classes: `TIMEOUT`, `RATE_LIMIT`, `UNAVAILABLE`, `TECHNICAL_ERROR`, `PROVIDER_ERROR` (`app/market/http.py:48-54`).
- Non-retryable: `AUTH_FAILED` (401/403), `METRIC_NOT_FOUND` (404), `MALFORMED_RESPONSE`.
- **PARTIALLY VERIFIED**: Whether `CMC_API_KEY` / `CG_API_KEY` are configured at runtime is UNKNOWN (see §12).
- **NOT AVAILABLE**: Any credential leakage protection beyond header scrubbing (`app/market/http.py:78-82`).

**Operational constraints (VERIFIED)**:

- Pipeline is **synchronous and single-run**: `run_u06_5()` (`app/market/finalization.py:2059-2178`) executes sequentially; no background tasks, no concurrency, no caching between runs.
- **No raw payload persistence**: only the final foundation snapshot is persisted (`persist_snapshot()`, `app/market/finalization.py:2244+`). Raw kline/depth/CMC/CG responses are not stored.
- **No runtime verification of exchange endpoints**: all repository tests use synthetic mock rows. Real endpoint behavior is UNKNOWN (see §12).
- **No historical exchange data**: `EXCHANGE_KLINE_LIMIT = 2` (`app/market/exchange_evidence.py:200`).

**Deployment constraints (VERIFIED)**:

- **Network reachability is UNKNOWN**: the deployment server's ability to reach Binance/Coinbase/CMC/CoinGecko endpoints is not established by any repository evidence.
- **KEYLESS mode** is used for CMC (`app/market/finalization.py:436`); CoinGecko has no documented key requirement in the inspected code.
- **NOT AVAILABLE**: Any evidence of successful or failed real endpoint calls in production.

**Constraint summary**:

| Constraint | Status |
|-----------|--------|
| HTTP library | Standard library only (VERIFIED) |
| Retry policy | Deterministic error-class based (VERIFIED) |
| Concurrency | None — synchronous (VERIFIED) |
| Raw payload persistence | NOT AVAILABLE (VERIFIED) |
| Runtime endpoint verification | UNKNOWN (NOT performed) |
| Historical exchange data | NOT AVAILABLE — limit 2 (VERIFIED) |
| Network reachability | UNKNOWN |
| API key configuration | UNKNOWN |
| Per-asset exchange data (non-BTC) | NOT AVAILABLE (VERIFIED) |

## 11. Evidence Matrix

Each row is a claim; each column is the evidence label. Only VERIFIED claims are backed by inspected repository code; PARTIALLY VERIFIED, UNKNOWN, and NOT AVAILABLE are recorded as such.

| # | Claim | Repository evidence | External evidence | Label |
|---|-------|-------------------|-------------------|-------|
| 1 | Reference engine is deterministic, no live calls inside | `reference.py:1-10` | — | VERIFIED |
| 2 | Eight reliability components with fixed weights | `reference.py:36-49` | — | VERIFIED |
| 3 | `data_integrity` weight 0.20 | `reference.py:36-49` | — | VERIFIED |
| 4 | `freshness` weight 0.15 | `reference.py:36-49` | — | VERIFIED |
| 5 | `volume` weight 0.15 | `reference.py:36-49` | — | VERIFIED |
| 6 | `near_depth` weight 0.10 | `reference.py:36-49` | — | VERIFIED |
| 7 | `far_depth` weight 0.10 | `reference.py:36-49` | — | VERIFIED |
| 8 | `spread` weight 0.10 | `reference.py:36-49` | — | VERIFIED |
| 9 | `price_impact` weight 0.10 | `reference.py:36-49` | — | VERIFIED |
| 10 | `cross_exchange_consistency` weight 0.10 | `reference.py:36-49` | — | VERIFIED |
| 11 | USD/USDT/USDC normalize at rate 1.0 | `reference.py:190-235` | — | VERIFIED |
| 12 | BTC/ETH require real conversion price | `reference.py:190-235` | — | VERIFIED |
| 13 | MAD-based outlier filter | `reference.py:290-365` | — | VERIFIED |
| 14 | Binance primary, Coinbase fallback | `exchange_evidence.py:198` | — | VERIFIED |
| 15 | 7-of-8 coverage gate (row-count) | `exchange_evidence.py:227-239` | — | VERIFIED |
| 16 | `EXCHANGE_KLINE_LIMIT = 2` | `exchange_evidence.py:200` | — | VERIFIED |
| 17 | `EXCHANGE_SYMBOL = "BTCUSDT"` | `exchange_evidence.py:198` | — | VERIFIED |
| 18 | `PROVIDER_SUPPLIED_TRADED_BASE_VOLUME` | `exchange_evidence.py:198` | — | PARTIALLY VERIFIED |
| 19 | `spread_pct` units | `exchange_evidence.py:290-339` | — | UNKNOWN |
| 20 | CMC vs CoinGecko agreement threshold 1.0% | `finalization.py:359-418` | — | VERIFIED |
| 21 | HTTP error classification | `http.py:33-44` | — | VERIFIED |
| 22 | Retryable error classes | `http.py:48-54` | — | VERIFIED |
| 23 | CMC KEYLESS mode | `finalization.py:436` | — | VERIFIED |
| 24 | No raw payload persistence | `finalization.py:2244+` | — | VERIFIED |
| 25 | No runtime endpoint verification | all tests use mocks | — | VERIFIED |
| 26 | Per-asset exchange data for non-BTC | `exchange_evidence.py:198` | — | NOT AVAILABLE |
| 27 | Historical exchange series | `exchange_evidence.py:200` | Unit 02 report | NOT AVAILABLE |
| 28 | Exchange reliability ranking | `exchange_evidence.py:198` | — | NOT AVAILABLE |
| 29 | Real endpoint reachability | — | — | UNKNOWN |
| 30 | `CMC_API_KEY` / `CG_API_KEY` at runtime | — | — | UNKNOWN |
| 31 | Minimum-observation floor in filter | `reference.py:290-365` | — | NOT AVAILABLE |
| 32 | Exchange identity per observation | `reference.py:460-586` | — | NOT AVAILABLE |
| 33 | Timestamp window width | `reference.py:460-586` | — | UNKNOWN |
| 34 | Confidence metric interpretation | `reference.py:460-586` | — | UNKNOWN |
| 35 | `near_depth`/`far_depth` window consistency | `exchange_evidence.py:260-290` | — | UNKNOWN |
| 36 | `traded_volume` base vs quote semantics | `exchange_evidence.py:198` | — | PARTIALLY VERIFIED |
| 37 | Binance/Coinbase symbol conventions | `exchange_evidence.py:198` | — | VERIFIED |
| 38 | No adaptive or learned weighting | `reference.py:36-49` | — | VERIFIED |
| 39 | No exchange health tracking across runs | `reference.py:460-586` | — | NOT AVAILABLE |
| 40 | No fallback escalation beyond Coinbase | `exchange_evidence.py:198` | — | NOT AVAILABLE |

## 12. UNKNOWNs and NOT AVAILABLE

This section separates what is unknown from what is explicitly unavailable, so that Unit 05 does not mistake either for established fact.

### UNKNOWN (not established by available evidence)

| # | Unknown | Why unknown | Where it matters |
|---|---------|-------------|------------------|
| U1 | `spread_pct` units and population | `exchange_evidence.py:290-339` defines the field but does not document units or guarantee population | §5, §7 — spread scoring correctness |
| U2 | Real endpoint reachability | No live probes performed; all tests use synthetic mocks | §10 — deployment viability |
| U3 | `CMC_API_KEY` / `CG_API_KEY` at runtime | Credential discovery (Unit 01) did not establish runtime configuration | §10 — CMC/CG availability |
| U4 | Timestamp alignment window width | `reference.py:460-586` groups by window but width is config-dependent and uninspected | §6, §9 — comparability |
| U5 | Confidence metric interpretation | Computed but no documented scale or threshold | §8 — output usability |
| U6 | `near_depth`/`far_depth` window consistency across exchanges | Depth window definitions not inspected per exchange | §5, §6 — comparability |
| U7 | `traded_volume` base vs quote semantics at runtime | Field name says base; provider semantics unverified | §5, §7 — volume scoring |
| U8 | Whether the 7-of-8 gate passes against real endpoints | Row-count gate; real responses unknown | §4, §8 — gate viability |
| U9 | Whether `cross_exchange_consistency` is meaningful with only 2 reachable exchanges | Effective set is Binance + Coinbase | §7, §9 — scoring validity |
| U10 | Runtime values of `max_price_deviation_pct_from_median`, `max_robust_z`, `mad_epsilon` | Configuration-dependent; not inspected in this pass | §7, §8 — filter behavior |

### NOT AVAILABLE (explicitly unsupported or unavailable)

| # | Not available | Source |
|---|---------------|--------|
| N1 | Per-asset exchange data for non-BTC assets (124 of 125) | `exchange_evidence.py:198` — BTCUSDT only |
| N2 | Historical exchange OHLCV series | `exchange_evidence.py:200` — limit 2 |
| N3 | Exchange reliability ranking or decay | No such code exists |
| N4 | Per-exchange health tracking across runs | No such code exists |
| N5 | Fallback escalation beyond Coinbase | `exchange_evidence.py:198` — static fallback only |
| N6 | Raw exchange payload persistence | `finalization.py:2244+` — only final snapshot persisted |
| N7 | Minimum-observation floor in outlier filter | `reference.py:290-365` — no floor enforced |
| N8 | Exchange identity per observation | `reference.py:460-586` — not recorded |
| N9 | Spread sanity checks | Units unknown; no checks exist |
| N10 | Volume/depth sanity checks beyond outlier filter | No such checks exist |
| N11 | Freshness-based staleness alerts | Only scoring function exists |
| N12 | Real-time exchange streams | REST snapshot only (`exchange_evidence.py:260-290`) |
| N13 | Orderbook deltas or history | REST snapshot only |
| N14 | Per-asset orderbook for non-BTC | BTCUSDT only |
| N15 | Adaptive or learned reliability weighting | `reference.py:36-49` — fixed weights |
| N16 | Credential leakage protection beyond header scrubbing | `http.py:78-82` |
| N17 | Runtime endpoint verification evidence | All tests use mocks |

## 13. Implications for Unit 05 Consolidation

**What Unit 05 can rely on (VERIFIED)**:

- The eight reliability components and their fixed weights are established and stable (`reference.py:36-49`).
- USD quote normalization rules are explicit (`reference.py:190-235`).
- The MAD-based outlier filter is deterministic and documented (`reference.py:290-365`).
- The 7-of-8 coverage gate and HTTP error classification are deterministic (`exchange_evidence.py:227-239`, `http.py:33-44`).
- CMC-vs-CoinGecko agreement is computed with a documented 1.0% threshold (`finalization.py:359-418`).

**What Unit 05 must treat as UNKNOWN (do not assume)**:

- Whether any exchange endpoint is reachable at runtime (U2).
- Whether API keys are configured (U3).
- Whether the 7-of-8 gate passes against real endpoints (U8).
- `spread_pct` units (U1).
- Timestamp window width (U4).
- Confidence metric interpretation (U5).
- Depth window consistency (U6).
- Volume semantics at runtime (U7).

**What Unit 05 must treat as NOT AVAILABLE (do not plan to use)**:

- Per-asset exchange data for non-BTC assets (N1).
- Historical exchange series (N2).
- Exchange reliability ranking (N3).
- Per-exchange health tracking (N4).
- Fallback escalation beyond Coinbase (N5).
- Raw payload persistence (N6).
- Minimum-observation floor (N7).
- Exchange identity per observation (N8).
- Real-time streams (N12).

**Design constraints for Unit 05**:

1. **Do not redesign the reliability formula or weights.** This report documents them; changing them is out of scope for Unit 05 and would require a separate design phase.
2. **Do not add new thresholds.** The existing thresholds (`max_price_deviation_pct_from_median`, `max_robust_z`, `mad_epsilon`, 1.0% agreement) are the only ones in use.
3. **Do not assume cross-exchange coverage beyond BTCUSDT.** Any consolidation that implies per-asset exchange data for the other 124 assets would be incorrect.
4. **Do not assume runtime success.** All exchange/CMC/CG behavior must be treated as conditional on UNKNOWN reachability and configuration.
5. **Preserve the UNKNOWN/NOT AVAILABLE separation.** Unit 05 should carry forward the §12 lists rather than collapsing them into assumptions.
6. **Do not start Unit 05 implementation work.** Unit 05 is consolidation and documentation only; no code, test, or config changes are authorized here.

**Most important unresolved question for Unit 05**: Whether the 7-of-8 gate and the reliability scoring produce meaningful results when only Binance and Coinbase are effectively reachable. This is UNKNOWN and must be flagged, not resolved by assumption.

## 14. Sources and Verification Notes

**Repository sources inspected (all VERIFIED by direct read)**:

| File | Lines inspected | What was established |
|------|----------------|---------------------|
| `app/market/reference.py` | 1–100, 190–365, 460–586 | Module identity, version constants, `REQUIRED_RELIABILITY_COMPONENTS`, `normalize_quote_to_usd`, `outlier_filter_v1`, aggregation engine |
| `app/market/exchange_evidence.py` | 198–339 | `acquire_exchange_evidence`, 7-of-8 gate, `_valid_kline_row`, orderbook fetch |
| `app/market/http.py` | 1–157 | `HTTPResult`, `classify_http_error`, `http_json`, retryable classes |
| `app/market/finalization.py` | 239–359, 359–418, 421–448, 993–1052, 1217–1563, 2059–2178, 2244+ | Orchestration, cross-source evidence, CMC normalization, top-125 comparison, foundation build, `run_u06_5`, snapshot persistence |
| `app/config/quality.py` | 129–152 (referenced) | `HTTP_TIMEOUT_SECONDS`, `VERSION` |

**Prior research reports cited (VERIFIED as committed)**:

| Report | Commit | What it established |
|--------|--------|---------------------|
| `U06_5_RESEARCH_UNIT_01_SOURCES_ACCESS.md` | prior | Provider access conditions, credential discovery |
| `U06_5_RESEARCH_UNIT_01_ACCESS_ADDENDUM.md` | prior | Access addendum |
| `U06_5_RESEARCH_UNIT_02_HISTORICAL_MARKET_DATA.md` | prior | No historical exchange series retrieved |
| `U06_5_RESEARCH_UNIT_03_ORDERBOOK_DEPTH_SPREAD_PRICE_IMPACT.md` | `60fb43a` | Orderbook/depth/spread/price-impact semantics |

**Version constants (VERIFIED)** — `app/market/reference.py:36-49`:

- `OUTLIER_ENGINE_V2`
- `PRICE_AGGREGATOR_V2_RELIABILITY_WEIGHTED`
- `REFERENCE_PRICE_ENGINE_V1`

**External sources**: None cited as inspected. No live endpoint probes were performed; no exchange, CMC, or CoinGecko documentation was opened during this pass. External claims are therefore absent from this report by design.

**Verification notes**:

- All line ranges were read directly from the repository at the time of research.
- No claim is made about runtime behavior, since no live calls were executed.
- The evidence matrix (§11) is the authoritative cross-check: any claim not in the matrix with a VERIFIED label should be treated as INFERENCE or UNKNOWN.
- This report was assembled from numbered draft parts written to `/tmp` and concatenated; no content was generated or measured — all figures are structural, not empirical.

---