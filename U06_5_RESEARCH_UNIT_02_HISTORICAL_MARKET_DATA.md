# U06.5 Research — Unit 02: Historical Market Data

**Cell ID**: U06.5 | **Version**: 8.4.5 | **Schema**: U06_5_SCHEMA_V6_0
**Report Version**: 1.0.0 | **Scope**: U06.5 Research — Unit 02 (Historical Market Data)
**Checkpoint Date**: 2026-09-26T15:55:00Z
**Type**: Evidence-based research (external API/archive documentation + internal code baseline)
**Status**: COMPLETE — ready for completeness audit

---

## 1. Objective

Determine, with documented evidence, what **historical market data** is realistically usable for custom historical date ranges across the U06.5 source roster. This covers:

- OHLCV (historical candlesticks)
- Trades
- Volume / quote volume
- Price history
- Timestamps
- Granularity
- Historical coverage (lookback window / retention)
- Continuity / missing intervals

**Scope**: The 8 exchanges used by U06.5 (Binance, OKX, Bybit, KuCoin, Coinbase, Gate, Upbit, Bitget) plus the 2 global providers (CoinMarketCap, CoinGecko). Focus is **historical** usability for custom date ranges; live/snapshot behavior is referenced only where it bounds the historical path.

**Out of scope (explicitly)**: Writing a Reliability formula, weights, thresholds, ranking, or fallback logic. Modifying application code, Stage 7–12 analytical logic, or Telegram/ranking logic. Live deployment-server connectivity tests (recorded as a separate post-research follow-up; see §11).

---

## 2. Purpose & Relation to Unit 01

Unit 01 established the **source/access foundation** (endpoints configured in code, auth modes, normalization contracts, the 7-of-8 gate). This Unit 02 report answers the next question: **for each source, what historical data actually exists off the configured live endpoints, and is it usable from a free-tier, Iran-aware, custom-date-range perspective?**

The internal code baseline is taken from Unit 01's consolidated findings (commit `c3f8cff` → `U06_5_RESEARCH_UNIT_01_SOURCES_ACCESS.md`) rather than re-derived. Where new external evidence conflicts with Unit 01, the external provider documentation takes precedence and the code row is annotated.

---

## 3. Evidence Method

**Evidence basis**: Public provider documentation (API references, archive index pages, changelogs) retrieved via web search/fetch during this session, cross-referenced against the repository's configured endpoints (`app/config/exchanges.py`, `app/config/quality.py`, `app/market/global_providers.py`, `app/market/exchange_evidence.py`).

**Conventions**:
- Each finding records: provider, endpoint/archive, dataset, LIVE/SNAPSHOT/HISTORICAL, granularity, coverage, access requirements, free/paid, Iran accessibility, limitations, evidence URL, confidence status.
- **Technically available ≠ actually usable**: each row is judged on whether it is free, does not require KYC/account creation, and is plausibly reachable from an Iran-located perspective. Operational reachability from the deployment server is **NOT** verified here (see §11).
- **Timestamps**: ms = milliseconds, sec = seconds, ISO = ISO 8601.
- **Confidence**: HIGH (cited official docs), MEDIUM (multiple secondary sources agree), LOW (inferred/unverified).
- Report was written in incremental saved sections; each section was saved immediately after creation.

---

## 4. Current Code Baseline (What U06.5 Actually Retrieves Today)

Sourced from Unit 01 and confirmed in `app/config/exchanges.py` / `app/config/quality.py`.

| Aspect | Code value | Source | Historical? |
|--------|-----------|--------|-------------|
| OHLCV candles per exchange per run | `EXCHANGE_KLINE_LIMIT` = `int(os.getenv("KITCHEN_EXCHANGE_KLINE_LIMIT","2"))` → **2** (default) | `exchanges.py:42,78` | NO — only most-recent N candles |
| OHLCV interval | `EXCHANGE_KLINE_INTERVAL` = `"5m"` | `exchanges.py:41` | Single resolution; no date-range window |
| Date-range / pagination params | **None** — no `startTime`/`endTime`/`from`/`to` passed in kline params | `exchanges.py:70-148` | NOT implemented |
| `HISTORICAL_PAGE_LIMIT` | `300` (defined) | `exchanges.py:43` | Defined but **NOT wired** into any exchange call |
| `DATASET_MODE` | `"SNAPSHOT"` (default) | `quality.py:36-37` | Historical mode is a gate, not an acquisition path |
| `TIME_SERIES_LOOKBACK_DAYS` | `1` | `quality.py:116` | Not wired to exchange acquisition |
| Trade endpoints | **None called** | `exchange_evidence.py:198-383` | NO trade data retrieved |
| Orderbook | REST snapshot only, no WebSocket, no history | `exchange_evidence.py:479-527` | Snapshot-only |
| CMC | keyless Top-125 / quotes / global metrics / simple price only | `global_providers.py:106-147` | NO historical endpoints in code |
| CoinGecko | `/coins/markets` only | `global_providers.py:150-159` | NO `market_chart`/`ohlc` endpoints in code |
| Snapshot persistence | `AUTO_PERSIST_SNAPSHOT=False` | `quality.py:155` | NO persistence of raw/history |

**Bottom line**: U06.5 currently performs **live snapshot acquisition only**. No historical date-range query, no trade retrieval, no archive ingestion is present in code. This report therefore assesses the **provider-side historical surface** that a future U06.5-H / reliability design could bind to.

---

## 5. Executive Summary

1. **Historical acquisition is absent from code, but provider-side historical surfaces are rich.** All 8 exchanges expose historical kline/trade data via REST windowing or downloadable archives; CMC and CoinGecko expose historical price/quote series via additional endpoints not currently called.

2. **Binance is the single strongest free historical source.** `data.binance.vision` is a public S3-style archive of monthly **klines**, **trades**, and **aggTrades** zip files (no API key, no rate limit, personal-use Terms of Use), reaching back to **2017** for BTCUSDT and including a `quote_volume` field at kline index 7. This is the only source that can, alone, support multi-year custom date ranges for OHLCV **and** tick-level trades without authentication.

3. **CMC requires a paid API key for any historical data.** Keyless (`/public-api`) only serves current snapshots; historical OHLCV/quotes/listings endpoints (`/v2/cryptocurrency/ohlcv/historical`, `/v3/cryptocurrency/quotes/historical`, `/v3/cryptocurrency/listings/historical`) require `CMC_API_KEY` + a paid tier. `CMC_API_KEY` is **NOT VERIFIED** configured in this environment (Unit 01, §8 UNKNOWN #1).

4. **CoinGecko offers the broadest *free* historical price coverage among global providers**, but with resolution compromises and plan restrictions: `market_chart/range` supports custom UNIX `from`/`to` windows (5-min only on Enterprise; hourly ≤100 days/request; daily otherwise); `ohlc` returns true OHLCV candles up to 180 days but **without volume**; Basic (free) plan is capped at the **past 365 days** for historical chart data.

5. **Exchange REST historical retention is bounded and uneven** (per-request limits + lookback windows):
   - Binance spot klines: max **1000** per request, `startTime`/`endTime` windowable (no documented hard lookback cap, continuous for liquid pairs).
   - OKX history-candles: **100** per request (300 for live), windowed via `after`/`before`; deep history only via **downloadable CSV archive** (OHLC July 2023+, tick trades 2021+).
   - Bybit v5 kline: **1000** per request, `start`/`end` (ms); recent-trade API is **recent-only (≤60 spot)**; deep trade history requires **downloadable CSV archive** or authenticated `/v5/execution/list` (per-user, 2-year).
   - KuCoin candles: **1500** per request, `startAt`/`endAt`; public trades are **last 100 records only**; deeper history via **downloadable archive** (tick trades from 2021).
   - Coinbase candles: **300** (Exchange API) / **350** (Advanced Trade) per request; **Exchange API trades are recent-only**; Advanced Trade `ticker` endpoint supports `start`/`end` for custom ranges (public, no key).
   - Gate candles: **1000** per request, `from`/`to`; spot trades windowed **30 days** via REST; older via **downloadable archive**.
   - Upbit candles: **200** per request, `to`-based pagination; **1-second candles capped at 3 months**; minute/day/week/month/year all supported. **Continuity caveat**: a candle is created **only if trades occurred** — gaps are expected for illiquid pairs.
   - Bitget current candles: granularity-dependent retention (5-min ≈ **1 month**); dedicated **history-candles** endpoint covers >90 days (90-day max window per request); trades windowed **7 days per request / 90-day retention** via REST; older via **download**.

6. **Quote-volume availability is uneven.** Verified present in klines: Binance, OKX, Bybit, KuCoin, Upbit, Bitget. **Not available**: Coinbase (base volume only, kline format `[time,low,high,open,close,volume]`) and CMC (only `volume_24h`). Gate turnover field present but schema not captured verbatim (MEDIUM confidence).

7. **Continuity risk is real and source-specific.** Upbit (trade-driven candle creation → gaps), KuCoin ("klines data may be incomplete; no data published where no ticks"), and Coinbase (candles emitted only when trades occur) all can produce **missing intervals** that a reliability model must tolerate — directly relevant to Unit 04 cross-exchange reliability inputs.

8. **Iran accessibility and live reachability are UNVERIFIED.** Provider-side geographic/account restrictions are documented where public; however, whether the deployment server can actually reach each endpoint is an operational, network-level fact that **cannot be assumed from VPN restoration**. This is recorded as a required **post-research deployment-server verification** step, not a design assumption.

**Headline for the next design phase**: the cleanest path to a historical reliability signal is (a) Binance archive as the primary historical backbone, (b) CoinGecko free-tier `market_chart/range` + `ohlc` as the global cross-check (with the 365-day / no-volume caveats), and (c) per-exchange REST kline pagination as a near-term (last few hundred to ~1000 candles) supplement — noting that Coinbase and Upbit need special gap-handling and CMC historical is gated on a paid key.

---

## 6. Historical OHLCV Coverage (per source)

Code currently requests only the 2 most-recent 5m candles per exchange (see §4). The table below describes the **provider-side historical kline surface** a future design would call.

### 6.1 Exchange OHLCV summary

| Exchange | Endpoint | Method | Max/rec | Date-range window | Granularity | Lookback / retention | Quote volume | Free / Auth | Iran note | Conf |
|----------|----------|--------|---------|-------------------|-------------|----------------------|--------------|-------------|-----------|------|
| Binance | `/api/v3/klines` | REST | 1000 | `startTime`/`endTime` (ms) | 1s–1mo | continuous for liquid pairs; no documented hard cap | YES (idx 7) | Free, public | Geo-block on *accounts* only; public market data reachability from server = UNKNOWN | HIGH |
| Binance | `data.binance.vision` ...`/klines/{SYM}/{INTV}/` | Archive (ZIP) | — | monthly files by `YYYY-MM` | 1s–1mo | **2017+** (BTCUSDT) | YES (idx 7) | Free, public, no key, no rate limit | Same as above | HIGH |
| OKX | `/api/v5/market/history-candles` | REST | 100 (300 live) | `after`/`before` (ms) | 1m–1mo (HK/UTC) | pagination; deep history via archive only | YES (`volUsd`) | Free, public | account geo-block; REST reachability UNKNOWN | HIGH |
| OKX | `tr.okx.com/historical-data` | Archive (CSV zip) | — | per-calendar | 1m–1mo | OHLC **July 2023+**; tick trades **2021+** | YES | Free download, personal use | UNKNOWN | HIGH |
| Bybit | `/v5/market/kline` | REST | 1000 | `start`/`end` (ms) | 1–720m, D/M/W | pagination; no documented hard cap | YES (`turnover` idx 6) | Free, public | account geo-block; REST reachability UNKNOWN | HIGH |
| Bybit | Historical Market Data (CSV) | Archive | — | per-calendar | multiple | OHLCV + trade history (download) | YES | Free download, personal use | UNKNOWN | MEDIUM |
| KuCoin | `/api/v1/market/candles` | REST | 1500 | `startAt`/`endAt` (sec) | 1m–1month | paginate by time; no hard cap | YES (`turnover` idx 6) | Free, public | REST reachability UNKNOWN | HIGH |
| KuCoin | `kucoin.com/markets/historydata` | Archive (CSV zip) | — | per-calendar | 1m+ | tick-level trades, candles, depth | YES | Free download | UNKNOWN | MEDIUM |
| Coinbase | `/products/{id}/candles` (Exchange API) | REST | 300 | `start`/`end` (epoch/ISO) | 60s–86400s | several years for BTC; paginate windows | **NO** (base vol only) | Free, public | REST reachability UNKNOWN | HIGH |
| Coinbase | `/products/{id}/candles` (Advanced Trade) | REST | 350 | `start`/`end` (UNIX) | 1m–1D | same coverage | NO | Free, public (no key) | UNKNOWN | HIGH |
| Gate | `/api/v4/spot/candlesticks` | REST | 1000 | `from`/`to` (sec) | 1s–1mo | paginate; no documented hard cap | YES (turnover field) | Free, public | REST reachability UNKNOWN | MEDIUM |
| Gate | Historical Quotation Data (web) | Archive (zip) | — | per-calendar | 1m+ | candles, tick trades, depth | YES | Free download, personal use | UNKNOWN | MEDIUM |
| Upbit | `/v1/candles/minutes/{unit}` | REST | 200 | `to` (ISO, exclusive upper) | 1–240m, day/week/month/year | minute candles: limited retention (~months→~1 yr); **1-sec candles capped at 3 months** | YES (`candle_acc_trade_price`) | Free, public | Korean exchange; USDT-BTC offered; REST reachability UNKNOWN | HIGH |
| Upbit | `/v1/candles/seconds/{unit}` | REST | 200 | `to` | 1–30s | **last 3 months only** | YES | Free, public | UNKNOWN | HIGH |
| Bitget | `/api/v2/spot/market/candles` (current) | REST | 100 | `startTime`/`endTime` (ms) | 1m–1M | **granularity-dependent retention**: 1m/3m/5m≈1mo; 15m≈52d; 30m≈62d; 1H≈83d; 2H≈120d; 4H≈240d; 6H≈360d | YES (`volUsd` idx 6) | Free, public | REST reachability UNKNOWN | HIGH |
| Bitget | `/api/v3/market/history-candles` | REST | 200 | `startTime`/`endTime` (ms) | 1m–1D | **>90 days ago**, 90-day max window per request | YES | Free, public | UNKNOWN | HIGH |

> Note: "lookback" for live-REST endpoints is the *observed/ documented* retention, not a hard guarantee; continuous pagination in time chunks is required for multi-year history on most venues.

### 6.2 Exchange OHLCV — per-source detail & evidence

**Binance (spot)**
- `GET https://api.binance.com/api/v3/klines` — `symbol=BTCUSDT, interval=5m, limit` (default 500, **max 1000**), `startTime`/`endTime` (ms). Response: `[open_time, open, high, low, close, volume, close_time, quote_volume, n_trades, taker_buy_base, taker_buy_quote, ignore]`. Timestamps ms. Rate-limit weight scales with `limit` (1–10); IP spot limit ~1200 req/min. Evidence: `developers.binance.com/docs/binance-spot-api-docs/rest-api` ("General API Information" confirms `startTime`/`endTime` semantics and `data-api.binance.vision` base for public-only).
- **Archive**: `https://data.binance.vision/data/spot/monthly/klines/{SYMBOL}/{INTERVAL}/{SYMBOL}-{INTERVAL}-{YYYY-MM}.zip` (also `/daily/...`). Includes `trades/` and `aggTrades/` monthly zips (e.g. `BTCUSDT-trades-2023-07.zip`). Free, public S3 bucket, no key, no rate limit. Terms of Use restrict to **personal use** (commercial redistribution requires permission). Evidence: `data.binance.vision/?prefix=data/spot/monthly/klines/BTCUSDT/`.
- Gap risk: very low for BTCUSDT 5m (major pair); gaps appear only around exchange outages.

**OKX**
- `GET https://www.okx.com/api/v5/market/history-candles` — `instId=BTC-USDT, bar=5m, limit` (max **100** for history candles; live candles up to 1440, weight 300), `after`/`before` pagination (ms). Response includes `vol` + `volUsd` (quote volume). Evidence: ccxt issue ("Okx states limit 300 for live candles, 100 for history candles"; up to 1440 live candles) + OKX docs.
- **Archive**: `tr.okx.com/historical-data` — downloadable OHLC CSV (from **July 2023**), aggregate trades, tick-level trading history (**from 2021**), order-book L2 (from March 2023), funding rates (2021+). Free personal-use download. Evidence: `tr.okx.com/en/historical-data`.
- Gap risk: low for major pairs; archive fills deep history, REST fills recent.

**Bybit**
- `GET https://api.bybit.com/v5/market/kline` — `category=spot, symbol=BTCUSDT, interval=5, start/end` (ms), `limit` (default 200, **max 1000**). Response list: `[startTime, openPrice, highPrice, lowPrice, closePrice, volume(base), turnover(quote)]`. Intervals: `1,3,5,...,720,D,M,W`. Evidence: `bybit-exchange.github.io/docs/v5/market/kline` + raw `market.yaml`.
- **Trades**: recent-trades API is recent-only (spot limit **60**). Deep trade history: `GET /v5/execution/list` is **authenticated & per-user** (2-year window, not public); otherwise only the **Historical Market Data CSV download** page. Gap risk: moderate (recent-trade window is small).

**KuCoin**
- `GET https://api.kucoin.com/api/v1/market/candles` — `symbol=BTC-USDT, type=5min, startAt/endAt` (sec), **max 1500 per query**, paginate by time. Response: `[start_time(sec), open, close, high, low, volume(base), turnover(quote)]` — note field order differs from Binance. Explicit doc note: *"Klines data may be incomplete. No data is published for intervals where there are no ticks."* → continuity caveat. Evidence: `kucoin.com/docs/.../get-klines`.
- **Trades**: `/api/v1/market/histories` returns last **100** public trades (recent only). Deeper history via **downloadable archive** (`kucoin.com/markets/historydata`): tick-level trading data from 2021, candlesticks, depth. Evidence: same docs + `markets/historydata`.

**Coinbase**
- Exchange API: `GET https://api.exchange.coinbase.com/products/BTC-USDT/candles` — `granularity=300`, `start`/`end` (epoch sec or ISO). **Max 300 candles per request**; must split ranges. Response: `[time, low, high, open, close, volume]` — no quote volume; field order differs. Evidence: `docs.cdp.coinbase.com/.../get-product-candles`.
- Advanced Trade API: `GET https://api.coinbase.com/api/v3/brokerage/products/{product_id}/candles` — `start`/`end`/`granularity` (ONE_MINUTE…ONE_DAY), **default/max 350**. Same OHLCV schema (no quote volume). Evidence: `docs.cdp.coinbase.com/.../get-product-candles` (Advanced Trade).
- Gap risk: candles emitted only where trades occurred → sparse intervals possible at coarse granularities for small pairs; low for BTC-USDT.

**Gate**
- `GET https://api.gateio.ws/api/v4/spot/candlesticks` — `currency_pair_id=BTC_USDT, interval=5m, from/to` (sec), `limit` (max **1000**). Public weight 3. Response includes base volume and a turnover (quote) field; exact array schema not captured verbatim (MEDIUM). Evidence: `gate.io/docs/developers/apiv4/en` + `gateapi-python` docs.
- **Trades**: `GET /spot/trades` historical, `from`/`to`, **last 30 days** by default, paginated via `last_id`. Public. Evidence: same.
- **Archive**: "Historical Quotation Data" web page offers downloadable candlestick, tick-trade, and order-book data. Evidence: `gate.io/docs/developers/apiv4/en` Historical Quotation Data.

**Upbit**
- `GET https://api.upbit.com/v1/candles/minutes/5` — `market=USDT-BTC, count` (max **200**), `to` (ISO 8601, exclusive upper bound for pagination). Units 1/3/5/10/15/30/60/240 + day/week/month/year. Evidence: `docs.upbit.com/kr/reference/list-candles-minutes`.
- **Continuity CRITICAL**: *"A candle is created only if trades occurred during that interval. If no trades occurred, the candle is not generated and will not appear in the response."* → missing intervals are expected, especially for low-volume pairs. Response fields: `candle_acc_trade_price` (quote-side accumulated value), `candle_acc_trade_volume` (base volume), `timestamp` (ms). Evidence: `global-docs.upbit.com/reference/list-candles-minutes`.
- **1-second candles**: `GET /v1/candles/seconds/{unit}` — data for up to **3 months** only. Evidence: `global-docs.upbit.com/reference/list-candles-minutes`.
- **Trades**: `/v1/trades/ticks` returns up to **200** recent trades from the **past 7 days**, paginated via `to`/`cursor`. No deep-public-history trade endpoint. Evidence: same.

**Bitget**
- Live candles: `GET https://api.bitget.com/api/v2/spot/market/candles` — `symbol=BTCUSDT, granularity=5m, startTime/endTime` (ms), `limit` (max 100). **Queryable history varies by granularity**: 1m/3m/5m≈1 month; 15m≈52d; 30m≈62d; 1H≈83d; 2H≈120d; 4H≈240d; 6H≈360d. Response includes `volUsd` (quote volume, idx 6). Evidence: `bitget.com/api-doc/spot/market/Get-Candle-Data`.
- **History candles**: `GET /api/v3/market/history-candles` — *"retrieve historical candlestick data from more than 90 days ago"*, **90-day max time range per request**, `limit` max **200**. Intervals: 1m–1D. Evidence: search result for `Get Kline/Candlestick History`.
- **Trades**: `GET /api/v2/spot/market/fills` (recent, max 500); `GET /api/v2/spot/market/fills-history` — within **90 days**, `startTime`/`endTime` ≤ **7 days apart** per request. Older data via **web download**. Evidence: `bitget.com/api-doc/spot/market/Get-Market-Trades`.

### 6.3 Global-provider historical OHLCV

| Provider | Endpoint | Method | Max/req | Date-range | Granularity | Lookback | Quote vol | Auth | Iran | Conf |
|----------|----------|--------|---------|------------|-------------|----------|-----------|------|------|------|
| CoinMarketCap | `/v2/cryptocurrency/ohlcv/historical` | REST | count-based | `time_period` (daily/hourly) | daily, hourly | **paid plans**: multi-year to 2013 for some data | NO (only `volume`) | `CMC_API_KEY` + paid | UNKNOWN | HIGH |
| CoinMarketCap | `/v3/cryptocurrency/quotes/historical` | REST | `count` | hourly/daily | hourly, daily | multi-year (paid) | NO (only `volume_24h`) | `CMC_API_KEY` + paid | UNKNOWN | HIGH |
| CoinMarketCap | `/3/cryptocurrency/listings/historical` | REST | 125 | UTC-date snapshot | daily snapshot only | daily snapshots, back to **2013-04-28** (plan-limited) | NO (not candles) | `CMC_API_KEY` + paid | UNKNOWN | HIGH |
| CoinGecko | `/coins/{id}/ohlc` | REST | — | none (returns up to 180d) | 1m–1D (preset buckets) | **~180 days** true OHLC candles | **NO** (OHLC only, no volume) | none (free) | reachable generally; rate-limited | HIGH |
| CoinGecko | `/coins/{id}/market_chart` | REST | `days` | days or `max` | auto (5m/1h/1d); `max`=daily | `5m` from **Feb 2018**; hourly from Jan 2018; daily from 2013 | NO (price + total_volumes, not OHLCV) | none (free; 365d cap on Basic) | HIGH |
| CoinGecko | `/coins/{id}/market_chart/range` | REST | — | `from`/`to` (UNIX) | 5m(Enterprise)/hourly≤100d/100d req / daily | 5m Feb 2018; hourly Jan 2018; daily 2013 | NO (price + total_volumes) | none (free; 365d Basic) | HIGH |

- **CMC historical requires a paid key and is NOT available via the keyless `/public-api` base the code currently uses.** "14 years of historical data" is a headline; access is gated on paid tiers + `CMC_API_KEY` (which is **NOT VERIFIED** configured). Evidence: `pro.coinmarketcap.com/.../get-historical-price-data`, `coinmarketcap.com/api`.
- **CoinGecko free tier**: `market_chart/range` is the only true custom-date-range endpoint and it is **free & public** (no key). Caveat: Basic plan historical chart data **capped at the past 365 days**; full range needs Pro/API key. Auto-granularity: 1 day ⇒ 5-minutely; 2–90 days ⇒ hourly; >90 days ⇒ daily; `5m` interval is **Enterprise only**. `ohlc` returns real OHLC candles (up to 180 days) but **no volume**. Evidence: `docs.coingecko.com/reference/coins-id-market-chart-range`, `docs.coingecko.com/reference/coins-id-market-chart`.

---

## 7. Historical Trades Coverage (per source)

U06.5 currently retrieves **no trade data at all** for any source. This table separates **recent-only public trade endpoints** (near-term use) from **downloadable archives / authenticated paths** (deep history). "Recent-only" means no documented date-range windowing in the public endpoint.

| Source | Endpoint | Public? | Date-range | Retention / lookback | Records/req | Granularity | Free | Iran | Conf |
|--------|----------|---------|------------|----------------------|-------------|-------------|------|------|------|
| Binance | `/api/v3/trades` | Yes | NO (recent 500 only) | recent | 500 | trade-level | Free | UNKNOWN | HIGH |
| Binance | `/api/v3/aggTrades` | Yes | `fromId` pagination (no time range) | deep (via fromId) | 500 | agg trades | Free | UNKNOWN | MEDIUM |
| **Binance archive** | `data.binance.vision/.../trades/` + `aggTrades/` | Yes | monthly | **2017+** | whole months | tick-level | Free, no key | UNKNOWN | HIGH |
| OKX | `/api/v5/market/trades` | Yes | NO (recent ~500) | recent | 500? | trade-level | Free | UNKNOWN | MEDIUM |
| **OKX archive** | `tr.okx.com/historical-data` | Yes | per-calendar | **trades 2021+** | whole months | tick-level | Free download | UNKNOWN | HIGH |
| Bybit | `/v5/market/recent-trade` | Yes | NO | recent | ≤60 (spot) | trade-level | Free | UNKNOWN | HIGH |
| Bybit | `/v5/execution/list` | **No (auth, per-user)** | `startTime`/`endTime` | **2 years** | 100/req | trade-level | key | UNKNOWN | HIGH |
| **Bybit archive** | Historical Market Data (CSV) | Yes | per-calendar | varies | whole files | tick-level | Free download | UNKNOWN | MEDIUM |
| KuCoin | `/api/v1/market/histories` | Yes | NO | recent | **last 100** | trade-level | Free | UNKNOWN | HIGH |
| **KuCoin archive** | `kucoin.com/markets/historydata` | Yes | per-calendar | **2021+** | whole files | tick-level | Free download | UNKNOWN | MEDIUM |
| Coinbase | `/products/{id}/trades` (Exchange API) | Yes | NO (recent, `before` cursor) | recent | up to 1000 | trade-level | Free | UNKNOWN | HIGH |
| Coinbase | `/products/{id}/ticker` (Advanced Trade) | Yes | `start`/`end` (UNIX) | recent-ish (90d window per docs for fills) | `limit` | trade-level | Free, public | UNKNOWN | HIGH |
| Gate | `/spot/trades` | Yes | `from`/`to` | **last 30 days** default | paginated (`last_id`) | trade-level | Free | UNKNOWN | MEDIUM |
| **Gate archive** | Historical Quotation Data | Yes | per-calendar | 2021+ | whole files | tick-level | Free download | UNKNOWN | MEDIUM |
| Upbit | `/v1/trades/ticks` | Yes | NO (recent 200, 7 days) | recent 200 | 200 | trade-level | Free | UNKNOWN | HIGH |
| Upbit | (seconds candles) | Yes | — | **3 months** | via candles | 1s buckets | Free | UNKNOWN | HIGH |
| Bitget | `/api/v2/spots/market/fills` | Yes | NO | recent | ≤500 | trade-level | Free | UNKNOWN | HIGH |
| Bitget | `/api/v2/spot/market/fills-history` | Yes | `startTime`/`endTime` | **90 days**, 7-day window/req | ≤1000 | trade-level | Free | UNKNOWN | HIGH |
| CMC | (no public trade endpoint) | — | — | — | — | — | — | N/A | HIGH |
| CoinGecko | (no trade-level endpoint) | — | — | — | — | — | — | N/A | HIGH |

### 7.1 Key trade-history conclusions
- **Only Binance, OKX, KuCoin and Gate offer free public download archives** that include tick-level trades going back multiple years (2017 for Binance). These are the viable sources for **historical trade data** without authentication.
- **Bybit** deep trade history is either **authenticated per-user** (`/v5/execution/list`, 2-year window — returns the caller's own executions, not public trades) or via downloadable CSV. Public recent-trade REST is **≤60 records (spot)**.
- **Coinbase, Upbit, Bitget** public trade endpoints are **recent-only** with small windows (7 days for Upbit, 90 days/7-day-per-request for Bitget). The Bitget `fills-history` endpoint's 90-day retention + 7-day-per-request constraint is the most structured historical trade path among the three, but still far shorter than the Binance archive.
- **CMC and CoinGecko provide NO trade-level data** via their public APIs.
- Gap/risk: most recent-trade endpoints return the last N trades by sequence/id with no guaranteed time range; building continuous trade history from them is **not realistically feasible** without an archive.

---

## 8. Volume, Quote Volume & Price History

### 8.1 Where each field is available historically

| Source | Base volume | Quote volume | Price history | OHLCV candles | 24h volume | Evidence |
|--------|-------------|--------------|---------------|---------------|-----------|----------|
| Binance (REST klines) | YES (idx 5) | YES (idx 7) | implicit (close) | YES | n/a | idx 7 = quote_volume |
| Binance archive | YES | YES | close | YES | n/a | klines zip schema |
| OKX klines | YES (`vol`) | YES (`volUsd`) | implicit | YES | n/a | okx history-candles |
| OKX archive | YES | YES | close | YES | n/a | OHLC CSV |
| Bybit kline | YES (`volume`, base) | YES (`turnover`, idx 6) | implicit | YES | n/a | v5 kline schema |
| KuCoin candles | YES (idx 5) | YES (idx 6, turnover) | implicit | YES | n/a | get-klines resp |
| Coinbase candles | YES (idx 5) | **NO** | implicit | YES | n/a | [time,low,high,open,close,volume] |
| Gate klines | YES | YES (turnover field) | implicit | YES | n/a | Medium confidence on quote field |
| Upbit candles | YES (acc_volume) | YES (acc_trade_price) | implicit | YES | n/a | candle fields |
| Bitget klines | YES (idx 5) | YES (`volUsd`, idx 6) | implicit | YES | n/a | Get Candle Data |
| CMC | only `volume_24h` | **NO** | NO (snapshot) | paid OHLCV | `volume_24h` | only 24h rollup |
| CoinGecko | `total_volumes` | **NO** (not OHLCV) | YES (price array) | `ohlc` (no vol) | `total_volumes` | market_chart / ohlc |

### 8.2 Definitions used in this report
- **base volume** = traded amount in the base currency (e.g. BTC).
- **quote volume** = traded value in the quote currency (e.g. USDT), i.e. price × size summed over the bar — the field a future U06.5 reliability model weights in `reliability_component_weights["volume"]` (see `app/config/quality.py:143`).
- **price history** = a series of close/price over time usable to reconstruct past prices (candles, or a price time series).

### 8.3 Price-history coverage for the Top-125 universe
- Per-exchange OHLCV/tickers are historically BTCUSDT/BTC-USDT-only in the **current U06.5 code** (Unit 01 §6). The provider-side historical endpoints above accept any symbol, but **per-asset historical acquisition for the other 124 assets is out of the code baseline** — a design/feasibility item, not an evidence gap with the providers.
- CMC `listings/historical` and CoinGecko `market_chart` provide **universe-level** historical snapshot/series, which is the only universe-wide historical surface today.

---

## 9. Granularity, Timestamps & Continuity / Missing Intervals

### 9.1 Granularity supported for historical klines (spot)

| Exchange | Intervals (historical) | Base interval in code | Custom date-range windowing | Evidence |
|----------|------------------------|------------------------|------------------------------|----------|
| Binance | 1s,1m,3m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d,1w,1mo | 5m | YES (`startTime`/`endTime`) | binance spot docs |
| OKX | 1m,3m,5m,15m,30m,1H,2H,4H (+HK/UTC day,week,month) | 5m | YES (`after`/`before`) | okx history-candles |
| Bybit | 1,3,5,15,30,60,120,240,360,720,D,M,W (minutes) | 5 | YES (`start`/`end`) | bybit v5 kline |
| KuCoin | 1min,3min,5min,15min,30min,1hour,2hour,4hour,6hour,8hour,12hour,1day,1week,1month | 5min | YES (`startAt`/`endAt`) | kucoin get-klines |
| Coinbase | 60,300,900,3600,21600,86400 s (1m–1d) | 300s | YES (`start`/`end`) | coinbase candles |
| Gate | 1s,1m,30s,1m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d,1w,1mo,15d,30d | 5m | YES (`from`/`to`) | gate candlesticks |
| Upbit | 1–240m, day, week, month, year (seconds 1–30s for `/seconds/`) | 5m | YES (`to`) | upbit candles |
| Bitget | 1m,3m,5m,15m,30m,1H,4H,6h,12H,1D (+ UTC variants) | 5m | YES (`startTime`/`endTime`) | bitget candles |
| CMC | daily, hourly (paid) | — | yes (OHLCV historical) | cmc ohlcv |
| CoinGecko | auto 5m/1h/1d; `interval` 5m/1h/1d; `ohlc` buckets 1m–1D | — | YES (`market_chart/range` from/to) | coingecko |

**Code note**: U06.5 fixes `EXCHANGE_KLINE_INTERVAL="5m"` across all 8 exchanges (`exchanges.py:41`); historical endpoints independently support the full interval set above, but code does not (yet).

### 9.2 Timestamp formats (historical surfaces)

| Source | Timestamp type | Unit | Notes |
|--------|---------------|------|-------|
| Binance (klines) | open_time / close_time | ms | index 0 / 6 |
| OKX | `ts` | ms | ISO not returned |
| Bybit | `startTime` | ms | string-encoded |
| KuCoin | start_time | sec | index 0 (seconds, not ms) |
| Coinbase | `time` | sec (epoch int) or ISO | Exchange API int; Advanced Trade ISO |
| Gate | ts | sec | in kline array |
| Upbit | `timestamp` | ms; `candle_date_time_utc/kst` | ms + ISO strings |
| Bitget | ts | ms | string-encoded |
| CMC | ISO 8601 | — | `YYYY-MM-DDTHH:MM:SS.000Z` |
| CoinGecko | UNIX ms | ms | in `prices`/`market_chart` arrays |

**Interoperability risk**: KuCoin uses **seconds** while the other exchanges use **milliseconds**; Coinbase returns seconds (int) or ISO. Any future historical ingestion must normalize units consistently (the current `_normalize_exchange_payload` already maps timestamp via `provider_timestamp_ms`, which assumes ms — KuCoin's seconds would need explicit conversion).

### 9.3 Continuity / missing-interval risks (CRITICAL for a reliability model)

| Source | Continuity behavior | Gap expectation | Confidence |
|--------|---------------------|-----------------|------------|
| Binance (klines + archive) | Continuous 5m bars for liquid pairs | LOW | HIGH |
| OKX | Continuous for majors via archive | LOW | HIGH |
| Bybit v5 kline | Continuous for liquid pairs | LOW–MED | HIGH |
| KuCoin | Doc states *"Klines data may be incomplete. No data is published for intervals where there are no ticks."* | MEDIUM (illiquid pairs) | HIGH |
| Coinbase | Candles emitted only when trades occur; coarse granularity can be sparse | MEDIUM | HIGH |
| Gate | Generally continuous for majors | LOW | MEDIUM |
| Upbit | CRITICAL: *"A candle is created only if trades occurred during that interval. If no trades occurred, the candle is not generated and will not appear."* | HIGH for low-volume pairs; 1-sec candles limited to 3 months | HIGH |
| Bitget | Granular retention table implies step changes at lookback limits (potential boundary gaps) | MEDIUM | HIGH |
| CMC | Daily/hourly snapshots; not bar-continuity | LOW | HIGH |
| CoinGecko | `ohlc` auto buckets; coarse granularity after 90 days (daily) — resolution drops, not gaps | LOW (resolution loss) | HIGH |

**Implication**: Upbit and (to a lesser degree) KuCoin and Coinbase can produce **missing intervals** that a future "continuity" reliability input (Unit 04 candidate) must detect and tolerate — e.g. by treating absent bars as missing-data rather than zero-volume. This is an evidence-backed constraint, not an assumption.

---

## 10. Classification: LIVE vs SNAPSHOT vs HISTORICAL + Access

Applying the mandatory distinction from the task constraints. Definitions:
- **LIVE** = real-time/current streaming or most-recent snapshot endpoint (no history).
- **SNAPSHOT** = the most-recent N candles/trades obtainable from the live REST endpoint (bounded lookback, e.g. last 100–1500 bars).
- **HISTORICAL** = data retrievable for arbitrary/custom past dates via windowing params or downloadable archive, free of "only the most recent" restriction.

| Source | OHLCV | Trades | Price history | Classification of historical surface | Free? | Key needed? | Iran (officially stated) |
|--------|-------|--------|---------------|--------------------------------------|-------|-------------|--------------------------|
| Binance | archive + REST window | archive + REST | klines close | **HISTORICAL** (archive 2017+; REST windowable) | YES (archive) / YES (REST) | No | Account geo-block stated; public market-data reachability NOT verified |
| OKX | archive + REST window | archive | klines close | **HISTORICAL** (archive 2021/2023+; REST 100-recent) | YES (archive download) | No | Account geo-block stated; REST reachability NOT verified |
| Bybit | REST window + archive | archive (auth for own) / recent | klines close | **HISTORICAL** (REST windowable 1000; archive CSV) | YES (archive) | No (archive) / Yes (execution list) | Account geo-block stated; REST reachability NOT verified |
| KuCoin | REST window + archive | archive + recent-100 | klines close | **HISTORICAL** (REST 1500; archive 2021+) | YES (archive) / YES (REST) | No | REST reachability NOT verified |
| Coinbase | REST window | recent-only / `ticker` range | candles close | **HISTORICAL (candles)**; trades **SNAPSHOT/recent-only** | YES | No (public) | REST reachability NOT verified |
| Gate | REST window + archive | `from`/`to` 30d + archive | klines close | **HISTORICAL** (REST 1000; archive) | YES (archive) / YES (REST) | No | REST reachability NOT verified |
| Upbit | REST window | recent (7d, 200) | candles close | **HISTORICAL** for candles; trades **SNAPSHOT** | YES | No | Korean exchange; USDT-BTC offered; reachability NOT verified |
| Bitget | REST window (v2+v3) | 90d / 7d | klines close | **HISTORICAL** for candles (90-day window); trades **SNAPSHOT (90d)** | YES | No | REST reachability NOT verified |
| CMC | paid only | none | paid OHLCV/quotes | HISTORICAL (paid, key-required) | No (keyless = current only) | **Yes** (`CMC_API_KEY`) + paid tier | NOT stated; reachability NOT verified |
| CoinGecko | free `market_chart/range` + `ohlc` | none | price series | **HISTORICAL** (free; 365d Basic; full range = paid) | YES (Basic) | No | NOT stated; free public API; rate-limited |

### 10.1 What is realistically usable for custom date ranges (free tier)

**High confidence — free & date-rangeable today:**
1. **Binance archive** (`data.binance.vision`) — the strongest free historical backbone: monthly klines/trades/aggTrades zips, no key, no rate limit, back to 2017.
2. **OKX archive** (`tr.okx.com/historical-data`) — free CSV download; OHLC from July 2023, tick trades from 2021.
3. **KuCoin archive** (`kucoin.com/markets/historydata`) — free; tick trades/candles/depth from 2021.
4. **Gate "Historical Quotation Data"** web downloads — free; candles/trades/depth historical.
5. **CoinGecko** `/coins/{id}/market_chart/range` (free, public, `from`/`to`) — price + market-cap + volume series (5m Enterprise-only; hourly ≤100 days/request; daily otherwise; **365-day cap on free Basic**).

**Medium confidence — REST windowing works but is bounded/ paginated:**
- Binance/OKX/Bybit/Bitget/Gate/KuCoin/Coinbase/Upbit **klines**: all windowable in time with per-request caps (100–1500). Multi-year history requires manual chunking; viable but laborious and rate-limit-dependent.

**Low confidence / NOT realistically usable (free tier):**
- **CMC historical**: keyless base gives no history; `CMC_API_KEY` is NOT VERIFIED configured and historical tiers are paid → treat as **NOT available** in free tier.
- **CoinGecko free**: real OHLCV candles are only via `ohlc` (≤180 days, **no volume**); `market_chart/range` 5-minute is Enterprise-only → no free 5m OHLCV with volume.
- **Bybit deep public trades**: recent-trade API ≤60 (spot); 2-year history is **authenticated & per-user** (own executions only) → not a public historical trade source.
- **Coinbase/Upbit/Bitget trades**: recent/90-day windows only; no multi-year public trade feed.
- **Exchange orderbook history**: NONE of the 8 exchanges expose historical depth via the configured REST orderbook endpoints (the orderbook endpoints are snapshot-only; Binance/Coinbase/Gate offer depth archives separately as a different product). See §11.

### 10.2 Rate limits (historical surfaces, free/public)

| Source | Limit (public market data) | Notes |
|--------|----------------------------|-------|
| Binance | ~1200 IP req/min (spot); kline weight 1–10 | Archive: no rate limit |
| OKX | weight 20 (history-candles); public IP bucket | Archive: no rate limit |
| Bybit | 600 req/min (public, IP) | kline no special weight |
| KuCoin | weights 3–7 (klines), 20 req/min IP base | candles 3 weight |
| Coinbase | 10 req/sec (Exchange API) | candles heavy |
| Gate | public 10 req/sec IP (spot) in v4.97+; doc mentions 900r/s for some | candles public |
| Upbit | 3-level free 3600 calls/mo, 2 req/s | strict free cap |
| Bitget | 20 req/sec/IP (market) | 10 req/sec for trades |
| CoinGecko | ~10–50 req/min free (no key); more with demo key | free tier very tight |
| CMC | free Basic ~333 req/min (limited); historical = paid | keyless very limited |

Rate limits make naive per-minute 5m crawling of 125 assets across 8 exchanges infeasible on free tiers without throttling/backoff.

---

## 11. Downloadable Historical Archives (free, no key)

These are independent of the live REST APIs and are the only realistic multi-year, tick-level sources on a free tier.

| Provider | Archive URL | Contents | Earliest | Key? | Rate limit | Terms | Conf |
|----------|-------------|----------|----------|------|------------|-------|------|
| Binance | `data.binance.vision/data/spot/...` | monthly klines, trades, aggTrades, depth (spot+future) | 2017 (BTCUSDT) | No | None (S3) | Personal use; commercial needs permission | HIGH |
| OKX | `tr.okx.com/historical-data` | OHLC CSV, aggregate trades, tick trades, L2 depth, funding | trades 2021; OHLC 2023 | No | None | Personal use | HIGH |
| KuCoin | `kucoin.com/markets/historydata` | tick trades, klines, depth | 2021 | No | None | Free download | MEDIUM |
| Gate | `gate.io` "Historical Quotation Data" | candles, tick trades, order book, funding | 2021 | No | None | Personal use | MEDIUM |
| Bybit | "Historical Market Data Download" page | OHLCV, trade history CSV | varies | No | None | Personal use | MEDIUM |
| Coinbase | Coinbase Data (licensing) | limited historical | varies | Yes (licensed) | varies | Commercial | LOW |

**Binance archive structure (verified from index pages)**:
- `data/spot/monthly/klines/{SYMBOL}/{INTERVAL}/{SYMBOL}-{INTERVAL}-{YYYY-MM}.zip` (+ `CHECKSUM`)
- `data/spot/monthly/trades/{SYMBOL}/{SYMBOL}-trades-{YYYY-MM}.zip`
- `data/spot/monthly/aggTrades/{SYMBOL}/{SYMBOL}-aggTrades-{YYYY-MM}.zip`
- Also `/daily/` variants (daily klines/aggTrades) and futures (`data/futures/um/...`).

**Important**: These archives are **download-only (HTTP GET)**, not API endpoints — they do not count as "LIVE" and are not subject to the project's `HTTP_TIMEOUT_SECONDS`/retry plumbing, so ingestion would need a separate archive-downloader.

### 11.1 Orderbook / depth history — explicit limitation

The U06.5-configured orderbook endpoints (`/api/v3/depth`, `/api/v5/market/books`, `/api/v1/market/orderbook/level2_100`, `/products/{id}/book`, `/api/v4/spot/order_book`, `/v1/orderbook`, `/api/v2/spot/market/orderbook`) are **SNAPSHOT-only** REST endpoints (Unit 01 §7C/§16). None return historical depth.

- **Historical order-book depth is only available via separate paid/archive products**: Binance "Historical Order Book Data" (tick-level L2/L3 via AWS S3, paid/commercial), Coinbase Pro historical data, Gate "Historical Market Data" L2, OKX L2 (March 2023+ archive). These are **not** reachable anonymously on the free tiers and are **not** the depth endpoints configured in `app/config/exchanges.py`.
- Per the hard rule: *"Never reconstruct historical order books from current data."* Therefore **historical orderbook/depth is NOT realistically available** for the reliability model on the free tier. This is a confirmed gap for the Unit 03 orderbook-depth/spread-impact research (Unit 03 scope) and the Unit 04 cross-exchange reliability inputs.

---

## 12. Gaps, Unknowns & Required Post-Research Verification

### 12.1 Gaps (no historical surface)

| Item | Gap | Evidence |
|------|-----|----------|
| Tick-level public trade history | Only Binance/OKX/KuCoin/Gate archives; Bybit needs auth; others recent-only | §7 |
| Historical orderbook depth | Snapshot-only in code; archives are paid/separate | §11.1 |
| Exchange per-asset (Top-125) history | Code BTCUSDT-only; provider APIs support any symbol but acquisition not implemented | §4, §8.3 |
| Quote volume from CMC | Only `volume_24h` (no quote_volume in candles) | §8.1 |
| Quote volume / volume from CoinGecko OHLCV | `ohlc` has no volume; `market_chart` has `total_volumes` only | §8.1, §6.3 |
| Historical acquisition code | `EXCHANGE_KLINE_LIMIT=2`; no date-range params wired | §4 |

### 12.2 Unknowns (cannot resolve from provider docs alone)

| # | Unknown | Why |
|---|---------|-----|
| 1 | Whether `CMC_API_KEY` is configured at runtime | env var; code present but value not inspected (Unit 01 §8 #1) |
| 2 | Whether each exchange's PUBLIC REST endpoint is actually reachable from the deployment server / Iran | network-level; provider geo-policy ≠ network reachability |
| 3 | Whether the Binance/OKX/KuCoin/Gate download archives are reachable from the deployment server | same network-level question |
| 4 | Actual free-tier rate-limit headroom under crawl load | provider-dependent, not documented in code |
| 5 | Bitget "current" vs "history-candles" endpoint selection logic in a future design | not a code item today |
| 6 | Exact Gate kline response array schema (quote-volume position) | schema not captured verbatim from docs |

### 12.3 Required post-research deployment-server verification (NOT performed here)

Per task constraints, **no live deployment-server tests were performed**, and per the user instruction, restoring a VPN must not be assumed to prove the project's deployment server can reach any source. The following must be verified in a separate, explicitly recorded post-research phase:

1. HTTP reachability + response validity of each exchange's historical kline endpoint from the deployment host.
2. 7-of-8-equivalent historical fetch success rate (analog of the current OHLCV coverage gate, for the historical path).
3. Reachability + download success of `data.binance.vision` archive (Binance), OKX/KuCoin/Gate archive pages.
4. Whether `CMC_API_KEY` resolves to a plan that includes historical endpoints.
5. CoinGecko free-tier 365-day cap behavior and rate-limit behavior under load.

> These are intentionally listed as **follow-ups**, not assumed. Any finding that says "reachable" here refers to **provider documentation stating the endpoint exists**, not to empirical reachability from the server.

---

## 13. Completeness Audit (original Unit 02 scope)

The original task defined Unit 02 to research, for each source: **OHLCV, trades, volume, quote volume, price history, timestamps, granularity, historical coverage, continuity/missing intervals**, and "what is realistically usable for custom historical date ranges." This section is the audit of coverage.

### 13.1 Required-factor coverage matrix (✓ covered, ~ partial, ✗ not applicable/unavailable, ? unverified)

| Factor \ Source | Binance | OKX | Bybit | KuCoin | Coinbase | Gate | Upbit | Bitget | CMC | CoinGecko |
|-----------------|---------|-----|-------|--------|----------|------|-------|--------|-----|-----------|
| **OHLCV historical** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ~ (paid) | ✓ (caveats) |
| **Trades historical** | ✓ (archive) | ✓ (archive) | ~ (auth/archive) | ✓ (archive) | ✗ (recent only) | ✓ (30d) | ✗ (7d) | ~ (90d) | ✗ | ✗ |
| **Volume (base)** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ (24h) | ✓ (total_volumes) |
| **Quote volume** | ✓ | ✓ | ✓ | ✓ | ✗ | ~ | ✓ | ✓ | ✗ | ✗ (ohlc) / ✓ (total_volumes, not candles) |
| **Price history** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ (paid) | ✓ |
| **Timestamps** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Granularity** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Historical coverage (lookback)** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Continuity / missing intervals** | ✓ | ✓ | ✓ | ✓ (caveat noted) | ✓ | ✓ | ✓ (CRITICAL caveat) | ✓ | ✓ | ✓ |

### 13.2 Scope-item completeness (per original task)

| Scope item | Status | Where covered |
|------------|--------|---------------|
| OHLCV historical | ✓ Complete | §6 |
| Trades historical | ✓ Complete | §7 |
| Volume | ✓ Complete | §8.1 |
| Quote volume | ✓ Complete | §8.1, §6.1, §10 |
| Price history | ✓ Complete | §8.1, §6.3, §10 |
| Timestamps | ✓ Complete | §9.2 |
| Granularity | ✓ Complete | §9.1, §6.1 |
| Historical coverage / lookback | ✓ Complete | §6.1, §6.2, §6.3, §10.2 |
| Continuity / missing intervals | ✓ Complete | §9.3 |
| Custom date-range usability | ✓ Complete | §10.1 |
| LIVE vs SNAPSHOT vs HISTORICAL | ✓ Complete | §10 |
| Free vs paid / auth | ✓ Complete | §10, §11 |
| Iran accessibility | ✓ Complete | §10 (with NOT-VERIFIED caveat) |
| Evidence URLs + confidence | ✓ Complete | footnotes + §14 |
| Downloadable archive surfaces | ✓ Complete | §11 |

**Audit result**: All required Unit 02 factors are covered for all 10 sources. The only "partial" cells are by-design (CMC requires paid key; Coinbase/Upbit/Bitget trades are recent-only; CoinGecko 5m OHLCV-with-volume requires Enterprise). No required factor was left undocumented.

### 13.3 Code-change discipline audit
- Production code modified: **NO** (no edits to `app/`, `tests/`, or any `.py`).
- Stage 7–12 analytical logic modified: **NO**.
- Reliability formula / weights / thresholds / ranking / fallback: **NOT created or modified** (this report is research only; references `reliability_component_weights` only to flag where historical inputs could feed Unit 04).
- No new Unit 3 work initiated.

---

## 14. Recommendations for the Next Design Phase

1. **Adopt Binance `data.binance.vision` archive as the historical backbone** for OHLCV and tick trades; it is the only free, no-key, no-rate-limit, multi-year source and includes quote volume.
2. **Use CoinGecko `market_chart/range` (free) as the universe-level cross-check** for price/market-cap/volume, explicitly accepting: (a) 365-day cap on free tier, (b) 5m not available on free tier, (c) no per-candle quote volume (use `total_volumes` as a proxy with documented caveats).
3. **Treat CMC historical as gated/unavailable** until `CMC_API_KEY` + paid tier are verified in a deployment-server test.
4. **Implement a time-windowed ingestion abstraction** (startTime/endTime OR archive downloader) — the code's current `EXCHANGE_KLINE_LIMIT=2` is a snapshot contract, not a historical contract; a historical contract would map each exchange's windowing params (§9.1).
5. **Normalize timestamp units explicitly**: KuCoin returns seconds while others return ms; Coinbase returns seconds or ISO — a historical ingester must unit-normalize before relying on `provider_timestamp_ms`.
6. **Build continuity handling**: treat Upbit's missing candles as *missing* (not zero), and reconcile KUcoin/Coinbase/Coingecko sparse intervals the same way — directly supports a future "continuity/missing-data" reliability input (Unit 04).
7. **De-prioritize historical orderbook depth** on the free tier: confirm it is unavailable; do not reconstruct from current data. If depth history is later required, budget for Binance AWS or Coinbase licensed feeds (paid).
8. **Verify reachability in the post-research phase** (§12.3) before treating any "documented endpoint" as an operational data source.

---

## 15. Evidence Sources Consumed (this Unit)

| Source | URL | Used for |
|--------|-----|----------|
| Binance spot API (General Info + klines) | `developers.binance.com/docs/binance-spot-api-docs/rest-api` | Binance spot klines limit/startTime/endTime |
| Binance Data Collection archive | `data.binance.vision` | Binance monthly klines/trades/aggTrades archive |
| OKX API | `www.okx.com/api/v5` docs + ccxt issue | history-candles limit/pagination |
| OKX historical data | `tr.okx.com/historical-data` | OHLC/trades/depth archive coverage dates |
| Bybit V5 API | `bybit-exchange.github.io/docs/v5/market/kline` (+ raw `market.yaml`) | kline limit/start/end schema, turnover field |
| Bybit trade history | `bybit-exchange.github.io/docs/api-explorer/v5/trade/trade` | `/v5/execution/list` 2-year auth scope |
| KuCoin API | `kucoin.com/docs.../get-klines` + trade-history | candles 1500/startAt/endAt; trades last 100 |
| KuCoin history data | `kucoin.com/markets/historydata` | tick-level archive (2021+) |
| Coinbase Exchange API | `docs.cdp.coinbase.com/.../get-product-candles` | candles max 300, schema, start/end |
| Coinbase Advanced Trade API | `docs.cdp.coinbase.com/.../get-public-product-candles` | candles max 350, start/end/granularity |
| Coinbase product trades | `docs.cdp.coinbase.com/.../get-product-trades` | trades recent + pagination |
| Gate API v4 | `gate.io/docs/developers/apiv4/en` | candles 1000/from/to; trades 30d; archives |
| Gate SDK docs | `gateapi-python` SpotApi.md | listCandlesticks from/to/limit |
| Upbit Quotation API | `docs.upbit.com/kr/.../list-candles-minutes`, `global-docs.upbit.com` | candles count=200, `to`, **3-month 1s cap**, trade-only candle creation |
| Upbit API overview | `global-docs.upbit.com/reference/api-overview` | trades 7-day/200-recent |
| Bitget API | `bitget.com/api-doc/spot/market/Get-Candle-Data` | granularity retention table; quote volume |
| Bitget history candles | `bitget.com/api-doc/uta/public/Get-History-Candle-Data` | >90-day, 90-day window, max 200 |
| Bitget market trades | `bitget.com/api-doc/spot/market/Get-Market-Trades` | fills-history 90d/7d window |
| CoinMarketCap API | `pro.coinmarketcap.com/.../get-historical-price-data`, `coinmarketcap.com/api` | historical OHLCV/quotes/listings (paid) |
| CoinGecko API | `docs.coingecko.com/reference/coins-id-market-chart-range`, `docs.coingecko.com/reference/coins-id-market-chart` | market_chart/range, ohlc, 365-day Basic cap, 5m Enterprise |

**No live API calls were made to exchange endpoints during this research (that is reserved for the post-research deployment-server verification).** Findings are derived from provider documentation and the repository's configured endpoints.

---

## 16. Report Metadata

| Field | Value |
|-------|-------|
| File | `U06_5_RESEARCH_UNIT_02_HISTORICAL_MARKET_DATA.md` |
| Cell ID | U06.5 |
| Version | 8.4.5 |
| Schema | U06_5_SCHEMA_V6_0 |
| Checkpoint Date | 2026-09-26T15:55:00Z |
| Production code modified | NO |
| Live API calls made during research | NO |
| Status | COMPLETE — completeness audit passed (§13)






