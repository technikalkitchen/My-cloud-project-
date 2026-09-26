# U06.5 Research — Unit 03: Orderbook Depth, Spread & Price Impact

**Cell ID**: U06.5 | **Version**: 8.4.5 | **Schema**: U06_5_SCHEMA_V6_0
**Report Version**: 1.0.0 | **Scope**: U06.5 Research — Unit 03 (Orderbook Depth / Spread / Price Impact)
**Checkpoint Date**: 2026-09-26T21:00:00Z
**Type**: Evidence-based research (internal code baseline + external provider documentation)
**Status**: COMPLETE — regenerated from verified repository sources

---

## 1. Objective

Determine, with documented evidence, what **orderbook depth, bid/ask spread, and price impact (slippage)** data is realistically usable across the U06.5 source roster, and how the existing U06.5 engine already computes these quantities. This covers:

- Orderbook snapshots (bids/asks, level counts, depth at multiple bands)
- Bid-ask spread (absolute, relative, in basis points)
- Price impact / slippage (simulated market order cost at fixed notionals)
- Depth bands (near depth vs far depth)
- Cross-exchange variation in depth, spread, and impact
- Freshness and continuity of orderbook evidence

**Scope**: The 8 exchanges used by U06.5 (Binance, OKX, Bybit, KuCoin, Coinbase, Gate, Upbit, Bitget). Orderbook acquisition and quality-metric computation are Layer A concerns; the reliability scoring that consumes these metrics is referenced only to trace data flow, not to introduce new formulas.

**Out of scope (explicitly)**: Writing a Reliability formula, weights, thresholds, ranking, or fallback logic. Modifying application code, Stage 7–12 analytical logic, or Telegram/ranking logic. Live deployment-server connectivity tests.

**Evidence basis**: Internal source code at `/workspaces/My-cloud-project-` (especially `app/market/reference.py`, `app/market/exchange_evidence.py`, `app/config/quality.py`, `app/config/exchanges.py`, `tests/unit/test_u06_5_unit_5_orderbook.py`), consolidated from prior U06.5 research checkpoints (Unit 01 Sources Access, Unit 02 Historical Market Data, Full Discovery Report, Runtime Source Map, Source & Historical Evidence Audit). External provider documentation is referenced where it bounds what is technically available. Live API responses were NOT captured.

---

## 2. Purpose & Relation to Prior Units

Unit 01 established the **source/access foundation** (10 endpoints configured in code, auth modes, normalization contracts, the 7-of-8 gate). Unit 02 established the **historical market-data surface** (OHLCV, trades, volume, continuity) and explicitly recorded that *historical orderbook depth is NOT realistically available* on the free tier — a confirmed gap that this Unit 03 report inherits and documents in detail.

This Unit 03 report answers: **for each exchange, what orderbook data exists off the configured live endpoints, what depth/spread/impact metrics the U06.5 engine already computes from that data, and what is missing or unavailable.**

The internal code baseline is taken from the consolidated findings of Units 01/02 and the Full Discovery Report rather than re-derived.

---

## 3. Evidence Method

**Evidence basis**: Internal source code, configuration constants, and test artifacts within the repository, cross-referenced against file paths, line numbers, and configuration constants. External provider documentation (API references, archive index pages) is referenced where it bounds what is technically available; these are marked separately from code evidence.

**Conventions**:
- Each finding records: provider, dataset, LIVE/SNAPSHOT/HISTORICAL classification, granularity, coverage, access requirements, free/paid, Iran accessibility, limitations, evidence URL/source, confidence status.
- **Technically available ≠ actually usable**: each row is judged on whether it is free, does not require KYC/account creation, and is plausibly reachable. Operational reachability from the deployment server is **NOT** verified here.
- **Confidence**: HIGH (cited official docs or direct code evidence), MEDIUM (multiple secondary sources agree), LOW (inferred/unverified).
- **No data fabrication**: explicit unavailable/error handling throughout; no synthetic depth, no interpolated levels, no silent resampling (source: `app/market/exchange_evidence.py:1-10`).

---

## 4. Current Code Baseline — What U06.5 Retrieves Today

Sourced from Unit 01 and confirmed in `app/config/exchanges.py` / `app/config/quality.py`.

| Aspect | Code value | Source | Historical? |
|--------|-----------|--------|-------------|
| Orderbook per exchange per run | REST snapshot, 100 levels | `exchanges.py:EXCHANGE_ORDERBOOK_LIMIT=100` | NO — snapshot only |
| Orderbook params | `limit=100` (Binance/Bybit/Coinbase/Gate/Bitget), `sz=100` (OKX), `markets=` (Upbit) | `exchanges.py:155-204` | NO |
| Date-range / pagination | **None** — no `from`/`to`/`startTime` in orderbook params | `exchanges.py:155-204` | NOT implemented |
| WebSocket streams | **None** — REST only | `exchange_evidence.py:479-527` | NO |
| Orderbook history | Snapshot-only; no historical depth endpoint configured | `exchange_evidence.py` | NOT AVAILABLE |
| Snapshot persistence | `AUTO_PERSIST_SNAPSHOT=False` | `quality.py:155` | NO |
| Depth bands computed | 0.05/0.10/0.25/0.50/1.00% from mid | `quality.py:137`, `reference.py:742` | Computed live only |
| Price impact notionals | $10,000 and $100,000 | `quality.py:139`, `reference.py:751` | Computed live only |

**Bottom line**: U06.5 currently performs **live orderbook snapshot acquisition only**. No historical depth, no streams, no per-asset orderbook (BTCUSDT-equivalent only). The engine *does* compute depth/spread/impact from each snapshot; those computations are the subject of §6–§9.---

## 5. Orderbook Acquisition Per Exchange (Unit 5)

### 5.1 Configuration (`app/config/exchanges.py`)

| Constant | Value | Source |
|----------|-------|--------|
| TARGET_EXCHANGE_COUNT | 8 | `exchanges.py:18` |
| MIN_VALIDATED_EXCHANGE_COUNT | 7 | `exchanges.py:19` |
| MULTI_EXCHANGE_PROBE_SYMBOL | "BTCUSDT" | `exchanges.py:23` |
| EXCHANGE_ORDERBOOK_LIMIT | 100 | `exchanges.py:78,160,167,...` |

### 5.2 Per-Exchange Orderbook Endpoints

Verified verbatim from `app/config/exchanges.py:155-204` (ORDERBOOK_SPECS dict).

| Exchange | Mode | Symbol | Orderbook URL | Params |
|----------|------|--------|--------------|--------|
| Binance | PUBLIC_SPOT | BTCUSDT | `https://api.binance.com/api/v3/depth` | symbol=BTCUSDT, limit=100 |
| OKX | PUBLIC_SPOT | BTC-USDT | `https://www.okx.com/api/v5/market/books` | instId=BTC-USDT, sz=100 |
| Bybit | PUBLIC_SPOT | BTCUSDT | `https://api.bybit.com/v5/market/orderbook` | category=spot, symbol=BTCUSDT, limit=100 |
| KuCoin | PUBLIC_SPOT | BTC-USDT | `https://api.kucoin.com/api/v1/market/orderbook/level2_100` | symbol=BTC-USDT |
| Coinbase | PUBLIC_SPOT | BTC-USDT | `https://api.exchange.coinbase.com/products/BTC-USDT/book` | limit=100 |
| Gate | PUBLIC_SPOT | BTC_USDT | `https://api.gateio.ws/api/v4/spot/order_book` | currency_pair_id=BTC_USDT, limit=100 |
| Upbit | PUBLIC_SPOT | USDT-BTC | `https://api.upbit.com/v1/orderbook` | markets=USDT-BTC |
| Bitget | PUBLIC_SPOT | BTCUSDT | `https://api.bitget.com/api/v2/spot/market/orderbook` | symbol=BTCUSDT, limit=100 |

**Symbol format divergence** (same as OHLCV): BTCUSDT (Binance/Bybit/Bitget), BTC-USDT (OKX/KuCoin/Coinbase), BTC_USDT (Gate), USDT-BTC (Upbit, reversed). All 8 are PUBLIC_SPOT; none require API keys.

### 5.3 Normalization Contract (`exchange_evidence.py:407-476`)

`_normalize_orderbook(exchange, spec, result)`:
- `_valid_orderbook_payload(payload)` (`exchange_evidence.py:390-404`): payload must be a dict with `bids` and `asks` lists, both non-empty, and every row a list with ≥2 elements whose price (index 0) and size (index 1) parse to non-None finite floats.
- Valid output: `{"exchange", "status": "VALIDATED", "selected_provider", "selected_provider_mode": spec["mode"], "fallback_used": False, "attempts": [{provider, provider_mode, endpoint, http_status, ok, valid: True, retrieved_at, error_class, error_message}], "bids": [{price, size}], "asks": [{price, size}]}`.
- Invalid/missing: `status: "NOT_AVAILABLE"`, empty bids/asks, attempt record with `valid: False` plus `error_class`/`error_message`. Provider-supplied depth is preserved exactly; no fabricated levels.

### 5.4 Acquisition Engine & Gate (`exchange_evidence.py:479-527`)

`acquire_multi_exchange_orderbook()`:
- Each exchange is an **independent parallel probe**. **No failover between exchanges.**
- `orderbook_engine`: `mode: "INDEPENDENT_PARALLEL_PROBES"`, `failover_between_exchanges: False`, `fabricated_depth: False`, `selection_used_for_current_top125: False`.
- Gate: `U06_5_UNIT_5_ORDERBOOK_COVERAGE`, `required = MIN_VALIDATED_EXCHANGE_COUNT (7)`, `target = TARGET_EXCHANGE_COUNT (8)`, `passed = validated_count >= 7`, status PASSED/FAILED.
- `volume_definition: "PROVIDER_SUPPLIED_TRADED_BASE_VOLUME"`; `probe_symbol: "BTCUSDT"`.

### 5.5 Test Evidence (`tests/unit/test_u06_5_unit_5_orderbook.py`)

4 deterministic tests (synthetic, no network):
- `test_u06_5_unit_5_valid_orderbook_response`: all 8 VALIDATED, `fabricated_depth` False, bids/asks lengths and values confirmed.
- `test_u06_5_unit_5_malformed_response_rejected`: OKX malformed → NOT_AVAILABLE, validated count = 7.
- `test_u06_5_unit_5_provider_failure`: Binance 503 → NOT_AVAILABLE, `attempts[0].valid` False, gate still passes at 7.
- `test_u06_5_unit_5_normalization_contract`: selected_provider/mode, `fallback_used` False, attempts structure, bids/asks values, engine mode confirmed.

### 5.6 LIVE vs SNAPSHOT vs HISTORICAL

All 8 exchanges: orderbook = **SNAPSHOT-only REST** (Unit 01 §7C/§16). No historical depth via configured endpoints. Classification of the *provider-side* historical depth surface: **NOT realistically available** on free tiers — see §12.---

## 6. Depth Bands — What Is Computed & How

### 6.1 Configuration (`app/config/quality.py:137`)

```python
"depth_bands_pct": (0.05, 0.10, 0.25, 0.50, 1.00)
```

### 6.2 Computation (`app/market/reference.py:673-690, 729-778`)

`orderbook_quality_metrics(book)` requires `book["status"] == "VALIDATED"` and a valid `mid_price`; otherwise returns `{"status": "NOT_AVAILABLE"}` (`reference.py:736-740`).

`_depth_usd(book, mid, band_pct, side)` (`reference.py:673-690`):
- `bound = band_pct / 100.0`
- Iterates `bids` (side="bid") or `asks` (side="ask"); for each level `[price, qty]`, if `|price - mid| / mid <= bound`, adds `price * qty`.
- Returns total USD for that side at that band.

Per band output: `{"bid_usd", "ask_usd", "total_usd"}` where `total_usd = bid_usd + ask_usd` (`reference.py:745-749`).

Bands produced: `0.05%`, `0.10%`, `0.25%`, `0.50%`, `1.00%`.

### 6.3 How Depth Is Consumed (`reference.py:367-453`)

In `_build_reliability_scores`:
- **near_depth** ← `depth_bands["0.10%"]["total_usd"]` (weight 0.20) at `reference.py:415-416`
- **far_depth** ← `depth_bands["1.00%"]["total_usd"]` (weight 0.10) at `reference.py:418-419`

Both scored via `_relative_log_score(value, peer_values)` (`reference.py:107-121`) — peer-normalized on `log1p`; zero/negative/None values are **unavailable, not zero-quality** (return None, excluded from the denominator at `reference.py:432-435`).

Peer pools are built from all validated observations: `near_peers` and `far_peers` collect each observation's corresponding band `total_usd`, filtered to `> 0` (`reference.py:381-388`).

### 6.4 Scope Limitation

Depth is computed **only for BTC**. `build_live_reference_price_from_multi_exchange()` is BTC/USDT-scoped (`reference.py:589-595`), and it is the only consumer of `orderbook_quality_metrics` in the current runtime path. Near/far depth for the other 124 Top-125 assets is **NOT PRESENT**. Depth beyond the 1.00% band is **NOT PRESENT** (only the five configured bands are computed). Depth time series is **NOT PRESENT** (no persistence; `AUTO_PERSIST_SNAPSHOT=False`, `quality.py:155`).

---

## 7. Spread — What Is Computed & How

### 7.1 Source

Spread is **not independently computed by the engine**; it is read from the orderbook record: `safe_float(book.get("spread_pct"))` at `reference.py:767`. It must be populated upstream (by the orderbook normalization/consumer). `orderbook_quality_metrics` converts it to basis points: `spread_bps = spread_pct * 100.0` (`reference.py:768-772`).

### 7.2 Scoring (`reference.py:133-137`)

```python
_spread_score(spread_bps) = bounded01(exp(-spread_bps / limit))
where limit = QUALITY_CONFIG["spread_soft_limit_bps"] = 20.0
```

`bounded01` clamps to [0,1]; None/negative → None (excluded from denominator). Weight in reliability: **0.10** (`quality.py:146`).

### 7.3 Gaps

Spread time series: NOT PRESENT. Mid-spread vs bid-ask spread distinction: **UNKNOWN** — depends on how `spread_pct` is populated upstream; the code reads it but does not compute it. Spread volatility: NOT PRESENT. Spread aggregation across exchanges: NOT computed (per-orderbook only). Whether `spread_pct` arrives populated and in what units (fraction vs bps) is an evidence gap — no upstream population site is verified in the supplied sources.

---

## 8. Price Impact / Slippage — What Is Computed & How

### 8.1 Configuration (`app/config/quality.py:139`)

```python
"price_impact_notional_usd": (10_000.0, 100_000.0)
```

### 8.2 Computation (`app/market/reference.py:693-726, 750-760`)

`_slippage_for_notional(book, mid, notional_usd, side)` (`reference.py:693-726`):
- Simulates a market order of `notional_usd` USD against the book (asks for "buy", bids for "sell").
- Walks levels, taking `min(remaining, price*qty)` per level, accumulating `acquired` (base) and `spent` (USD).
- If `remaining > 1e-6` (book too shallow to fill) or `acquired <= 0` → returns **None** (explicitly NOT fabricated).
- Else `avg_price = spent / acquired`; for "buy" returns `max(0, (avg_price - mid)/mid * 100)`; for "sell" returns `max(0, (mid - avg_price)/mid * 100)`.

Per notional output: `{"buy_pct", "sell_pct", "worst_pct"}` where `worst_pct = max(buy, sell)` (`reference.py:754-759`).

### 8.3 Scoring (`reference.py:140-144`)

```python
_impact_score(impact_pct) = bounded01(1.0 / (1.0 + impact_pct / 0.10))
```

Weight in reliability: **0.10** (`quality.py:147`). In `_build_reliability_scores`, the representative impact used is `min(impact_values)` across available notionals (`reference.py:400-404`).

### 8.4 Gaps

Price impact for non-BTC assets: NOT PRESENT (BTC-scoped engine). Price impact time series: NOT PRESENT. Actual execution costs: NOT PRESENT (no live trading; `TRADING_ENABLED=False`, `quality.py:160`). Exchange-reported price impact: NOT retrieved (all computed internally from the orderbook snapshot).---

## 9. Reliability Components Consuming Depth/Spread/Impact

### 9.1 Weights (`app/config/quality.py:140-149`) — sum = 1.00

| Component | Weight | Source value | Scoring function | Source |
|-----------|--------|--------------|------------------|--------|
| data_integrity | 0.15 | fixed 1.0 | constant | `reference.py:412` |
| freshness | 0.10 | orderbook `age_seconds` | `_freshness_score` = `bounded01(exp(-ln2 * age / half_life))`, half_life = `max_source_age_seconds/2` | `reference.py:124-130` |
| volume | 0.15 | `volume_usd_24h` | `_relative_log_score(value, peer_values)` | `reference.py:414` |
| near_depth | 0.20 | `depth_bands["0.10%"]["total_usd"]` | `_relative_log_score` | `reference.py:415-416` |
| far_depth | 0.10 | `depth_bands["1.00%"]["total_usd"]` | `_relative_log_score` | `reference.py:418-419` |
| spread | 0.10 | `spread_bps` | `_spread_score` = `bounded01(exp(-spread_bps/20.0))` | `reference.py:133-137` |
| price_impact | 0.10 | `worst_pct` at notionals | `_impact_score` = `bounded01(1.0/(1.0 + impact_pct/0.10))` | `reference.py:140-144` |
| cross_exchange_consistency | 0.10 | `|price - consensus|/consensus` | `bounded01(1.0/(1.0 + deviation/0.25))` | `reference.py:423-425` |

### 9.2 Missing-Feature Handling (`reference.py:427-442`)

If a component value is None, it is **excluded from the denominator** (reported `"status": "NOT_AVAILABLE", "weight_excluded": True`) — **never fabricated**. Score = `numerator / denominator` if denominator > 0 else 0.0, clamped to [0,1] by `_bounded01` (`reference.py:442, 101-104`).

### 9.3 Validation (`reference.py:54-94`)

`validate_reliability_weights()` asserts all 8 required components present (`REQUIRED_RELIABILITY_COMPONENTS`, `reference.py:40-49`), weights finite and non-negative, sum ≈ 1.0 (epsilon `1e-6`).

### 9.4 Aggregation (`reference.py:460-586`)

Pipeline: `validate_market_observation` (`reference.py:238-269`) → `outlier_filter_v1` (MAD; rejects `pct_dev > 5.0%` or `|robust_z| > 6.0`, `reference.py:285-360`) → require `>= min_markets_for_aggregate` (1) → require `>= min_reference_exchanges` (2) → `_build_reliability_scores` → weighted sum:

```
reference_price = SUM(normalized_usd_price * reliability * liquidity_signal) / SUM(reliability * liquidity_signal)
liquidity_signal = sqrt(max(0, log1p(volume) * log1p(near_depth)))  (or 1.0 if both missing)
```

`reference.py:526-538`. Confidence = `0.55 * mean_reliability + 0.25 * agreement + 0.20 * coverage` (`reference.py:557-561`). `single_exchange_is_not_cross_exchange_confirmed = len(scored) < 2` (`reference.py:584`).

### 9.5 BTC-Scoped

`build_live_reference_price_from_multi_exchange()` (`reference.py:589-666`) builds the BTC reference price from OHLCV close + quote_volume (derived as `base_volume * price` if quote_volume missing, `reference.py:608-611`) plus `evidence["orderbook_quality"]`. `not_global_market_cap: True`. **BTC/USDT only.**---

## 10. Cross-Exchange Variation in Depth, Spread & Impact

### 10.1 What Is Measured

`_build_reliability_scores` (`reference.py:367-453`) computes, per validated exchange observation: `consensus` = median of normalized USD prices (`reference.py:390-392`); per-exchange `price_deviation_pct` (`reference.py:406-409`); and per-exchange reliability scores for near_depth, far_depth, spread, and price_impact against **peer pools** (all validated observations' values). This is the mechanism that turns raw cross-exchange depth/spread/impact differences into a scored, comparable signal. Peer pools are filtered to values `> 0` (`reference.py:386-388`).

### 10.2 Agreement Thresholds (`app/config/quality.py:110-111, 124`)

`REFERENCE_MAX_PRICE_DEVIATION_PCT = 1.0`, `REFERENCE_MIN_OVERLAP = 0.80`, `REFERENCE_REQUIRED_FOR_LOCK = False`. Cross-source evidence (`build_provider_cross_source_evidence`, `finalization.py:359-418` per the Full Discovery Report) compares CMC vs CoinGecko per symbol; reference validation does NOT modify the foundation (`does_not_modify_foundation: True`).

### 10.3 Gaps

Cross-exchange depth/spread/impact matrices: NOT computed. Latency-adjusted comparison: NOT computed. Cross-exchange consistency for non-BTC assets: NOT PRESENT (reference engine is BTC-scoped). Historical cross-exchange agreement: NOT PRESENT.

---

## 11. Freshness & Continuity of Orderbook Evidence

### 11.1 Freshness

`orderbook_quality_metrics` computes `age_seconds = timestamp_age_seconds(book["source_timestamp"], book["retrieved_at"])` (`reference.py:761-763`). `QUALITY_CONFIG["max_orderbook_age_seconds"] = 30.0` (`quality.py:136`). This age feeds the `freshness` reliability component (weight 0.10). Freshness status for global data: FRESH ≤ 900s / STALE > 900s / UNAVAILABLE (`global_providers.py:264-274`).

### 11.2 Continuity

Orderbook is a **REST snapshot, not a stream** (`exchange_evidence.py:479-527`). No sequence IDs, no update IDs, no delta tracking are normalized or persisted. Orderbook stream persistence: NOT PRESENT. Orderbook sequence tracking: NOT PRESENT. Historical orderbook reconstruction: NOT PRESENT.

### 11.3 Continuity Risk (inherited from Unit 02 §9.3)

Provider-side orderbook endpoints are snapshot-only for all 8 exchanges. Historical order-book depth is only available via **separate paid/archive products** (Binance "Historical Order Book Data" via AWS S3 paid/commercial; Coinbase Pro historical data; Gate Historical Market Data L2; OKX L2 from March 2023 archive) — **not reachable anonymously on free tiers**, and **not** the depth endpoints configured in `app/config/exchanges.py`. Per the hard rule *"Never reconstruct historical order books from current data,"* historical orderbook/depth is **NOT realistically available** for the reliability model on the free tier.---

## 12. Gaps, Unknowns & Required Post-Research Verification

### 12.1 Gaps (no orderbook-depth surface)

| Item | Gap | Evidence |
|------|-----|----------|
| Historical orderbook depth | Snapshot-only in code; archives are paid/separate | §11.3 |
| Per-asset orderbook (Top-125) | Code BTCUSDT-equivalent only; provider APIs support any symbol but acquisition not implemented | §5.2 |
| Orderbook streams / deltas | REST only, no WebSocket | §11.2 |
| Depth beyond 1.00% band | Not computed | §6.4 |
| Depth/spread/impact for non-BTC | Reference engine BTC-scoped only | §6.4, §8.4 |
| Depth/spread/impact time series | Not persisted | §6.4, §8.4, §7.3 |
| Exchange API key auth for orderbook | All 8 are PUBLIC_SPOT | §5.2 |

### 12.2 Unknowns (cannot resolve from supplied sources)

| # | Unknown | Why |
|---|---------|-----|
| 1 | Whether `CMC_API_KEY`/`CG_API_KEY` configured at runtime | env vars; code discovery logic exists (`quality.py:74-94`) but values not inspected |
| 2 | Whether each exchange's public orderbook REST endpoint is reachable from the deployment server / Iran | network-level; provider geo-policy ≠ network reachability |
| 3 | Whether the 7-of-8 orderbook gate passes with real exchange data | Tests use synthetic mock rows; no live probe results captured |
| 4 | Actual orderbook response schema deviations vs `_valid_orderbook_payload` expectations | Tests use expected format; real-world deviations not tested |
| 5 | Total latency of full 8-exchange orderbook probe | No runtime timing data captured |
| 6 | Empirical basis for `MIN_VALIDATED_EXCHANGE_COUNT=7` | No documented rationale |
| 7 | Whether `spread_pct` is populated upstream and in what units (fraction vs bps) | Code reads it (`reference.py:767`) but population site not verified |

### 12.3 Required post-research deployment-server verification (NOT performed here)

Per task constraints, no live deployment-server tests were performed, and VPN restoration must not be assumed to prove reachability. Required follow-ups: (1) HTTP reachability + response validity of each exchange's orderbook endpoint from the deployment host; (2) 7-of-8-equivalent orderbook fetch success rate; (3) whether `spread_pct` arrives populated and correctly scaled; (4) actual orderbook age/latency under load vs the 30s soft limit.---

## 13. Completeness Audit (original Unit 03 scope)

The task defined Unit 03 to research, for each source: **orderbook depth, spread, price impact**, plus cross-exchange variation, freshness, and continuity. Audit of coverage.

### 13.1 Required-factor coverage matrix (✓ covered, ~ partial, ✗ not applicable/unavailable, ? unverified)

| Factor \ Source | Binance | OKX | Bybit | KuCoin | Coinbase | Gate | Upbit | Bitget |
|-----------------|---------|-----|-------|--------|----------|------|-------|--------|
| Orderbook snapshot | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Depth bands (5) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Price impact ($10k/$100k) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Spread (bps) | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ |
| Cross-exchange variation | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Freshness (age) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Continuity / history | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Free / auth | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Iran accessibility | ? | ? | ? | ? | ? | ? | ? | ? |

> "~ spread": spread is read from `book["spread_pct"]` whose upstream population is unverified (§7.3, Unknown #7). "✗ continuity/history": all 8 are snapshot-only with no historical depth on free tier (§11.3). "✓" rows are computed identically across all 8 exchanges via the shared `orderbook_quality_metrics` engine (`reference.py:729-778`); no per-exchange differences are coded.

### 13.2 Scope-item completeness

| Scope item | Status | Where covered |
|------------|--------|---------------|
| Orderbook acquisition + normalization | ✓ Complete | §5 |
| Depth bands (near/far) | ✓ Complete | §6 |
| Spread (absolute/relative/bps) | ✓ Complete (with caveat) | §7 |
| Price impact / slippage | ✓ Complete | §8 |
| Reliability components consuming them | ✓ Complete | §9 |
| Cross-exchange variation | ✓ Complete | §10 |
| Freshness | ✓ Complete | §11.1 |
| Continuity / missing intervals | ✓ Complete | §11.2-11.3 |
| LIVE vs SNAPSHOT vs HISTORICAL | ✓ Complete | §5.6, §11.3 |
| Free vs paid / auth | ✓ Complete | §5.2, §12.1 |
| Iran accessibility | ✓ Complete (NOT-VERIFIED) | §12.2 |
| Evidence URLs + confidence | ✓ Complete | footnotes + §13 |
| Gaps / unknowns | ✓ Complete | §12 |

**Audit result**: All required Unit 03 factors are covered for all 8 exchanges. The only "partial" cell is spread (by-design: the engine reads `spread_pct` from the upstream orderbook record rather than computing it). The only "not applicable" cells are historical depth (confirmed unavailable on free tier per Unit 02 §9.3). No required factor was left undocumented.

### 13.3 Code-change discipline audit

- Production code modified: **NO**.
- Stage 7–12 analytical logic modified: **NO**.
- Reliability formula / weights / thresholds / ranking / fallback: **NOT created or modified** (this report references existing `reliability_component_weights` and scoring functions only to trace data flow).
- No new Unit 4 work initiated.
- Live API calls made: **NO**. Web searches performed: **NO** (all evidence is internal code + previously documented provider findings from Units 01/02).

---

## 14. Recommendations

1. **Keep orderbook acquisition as snapshot-only by design** — it is the only free path; do not attempt WebSocket streams or historical depth reconstruction (violates the no-reconstruction rule and free-tier constraints).
2. **Verify `spread_pct` provenance upstream** — the engine consumes it but does not compute it; confirm units (fraction vs bps) and population site before relying on the spread score.
3. **Treat orderbook age as a hard gate** — enforce `max_orderbook_age_seconds = 30.0` explicitly at acquisition, since a stale snapshot silently degrades 3 reliability components (freshness, near_depth, far_depth).
4. **Document the BTC-scope limitation** — depth/spread/impact scores apply to BTCUSDT only; do not feed them as per-asset signals for the other 124 Top-125 assets.
5. **Record the historical-depth gap explicitly** for downstream reliability design — historical orderbook depth is NOT available on free tiers; any Unit 04 continuity/missing-data input must treat absent depth as missing, never zero.
6. **Persist the deployment-server verification list** (§12.3) as a separate follow-up; do not fold reachability assumptions into this report.

---

## CLASSIFICATION SUMMARY

| Category | Items |
|----------|-------|
| **IMPLEMENTED / FOUND** | 8-exchange orderbook snapshot acquisition with 7-of-8 gate; independent parallel probes; no failover; no fabricated depth; normalization contract (bids/asks [{price, size}]); 5 depth bands at 0.05/0.10/0.25/0.50/1.00%; price impact at $10k/$100k notionals with explicit no-fill → None; spread read in bps with exp(-bps/20) scoring; reliability components near_depth(0.20)/far_depth(0.10)/spread(0.10)/price_impact(0.10) with missing-feature denominator renormalization; MAD outlier filter; min 2 cross-exchange confirmation; 4 unit tests |
| **NOT FOUND** | Historical orderbook depth (free tier); per-asset orderbook for Top-125; orderbook streams/deltas; depth beyond 1.00%; depth/spread/impact for non-BTC; depth/spread/impact time series; orderbook sequence tracking; U06.5-specific manifests/audits/ledgers; persisted orderbook snapshots |
| **UNCERTAIN / NEEDS REVIEW** | `spread_pct` upstream population and units; whether `CMC_API_KEY`/`CG_API_KEY` configured; whether 8 orderbook endpoints reachable from deployment server/Iran; whether 7-of-8 orderbook gate passes empirically; response schema deviations; total probe latency; empirical basis for MIN_VALIDATED_EXCHANGE_COUNT=7 |

---

**Report Generated**: 2026-09-26T21:00:00Z
**Discovery Scope**: Complete repository search for U06.5 orderbook depth / spread / price impact
**Sources Used**: `app/market/reference.py`, `app/market/exchange_evidence.py`, `app/config/quality.py`, `app/config/exchanges.py`, `tests/unit/test_u06_5_unit_5_orderbook.py`, plus U06.5 Unit 01 and Unit 02 research reports
**No Files Modified**: Research-only; no production code, tests, or configuration changed
**Evidence Gaps**: Items marked UNKNOWN in §12.2; no claim was filled from general knowledge