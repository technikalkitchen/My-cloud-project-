# U06.5 Unit 01 — Access Addendum

**Cell ID**: U06.5 | **Version**: 8.4.5 | **Schema**: U06_5_SCHEMA_V6_0
**Date**: 2026-09-26T14:28:00Z
**Type**: Practical access assessment (supplements `U06_5_RESEARCH_UNIT_01_SOURCES_ACCESS.md`)
**Scope**: Market-data API access feasibility, auth, limits, and geographic/Iran restrictions only. No historical-depth analysis. No ranking/formula changes. No code modifications.

---

## 1. Priority Summary

| Priority | Providers | Rationale |
|----------|-----------|-----------|
| **1 — No account, no key, fully automatic** | Binance (market data), CoinMarketCap (keyless), CoinGecko (demo), Bybit*, KuCoin, Coinbase, Gate, Upbit*, Bitget, CoinPaprika | Public endpoints, no auth; bot fetches data with zero user action |
| **2 — Free key, one-time setup** | CMC Basic (free key), CoinGecko Demo key, CryptoCompare (free signup post-May-2026) | Registration yields API key; bot then runs automatically |
| **3 — VPN/alternate routing needed** | Bybit (Iran), OKX (Iran) | Documented service exclusion for Iran; exit node in an allowed country may restore access |
| **4 — Paid-only** | CoinGlass ($29/mo+), CryptoQuant (subscription) | No anonymous/free tier; not a primary path |

\* See Iran/geographic notes below.

> **Project evidence**: The original scanner retrieved data without credentials. This confirms public-access APIs can work, but each provider below must be evaluated individually — past success does not guarantee current access.

---

## 2. Provider-by-Provider Assessment

### 2.1 Binance

| Field | Value |
|-------|-------|
| **Access class** | no-account (public market data) |
| **Account/KYC** | Not required for market data. API key only needed for trading/account endpoints. |
| **Endpoint access vs website** | Separate **market-data-only** host `data-api.binance.vision` serves the same public endpoints (`/api/v3/klines`, `/api/v3/depth`, etc.) with no auth. This is distinct from the account/trading host `api.binance.com`. |
| **Free tier & limits** | No account needed. Rate limit: 6,000 request-weight/minute per IP; `/api/v3/klines` costs weight 2. HTTP 429 on breach; repeat offenses → HTTP 418 IP ban (2 min–3 days). |
| **Iran restriction** | Documented (account/trading). Binance Senate response (Mar 2026): "prohibits users located in Iran from accessing the platform." Voluntary IP block for compliance. **API-level market-data restriction**: NOT VERIFIED — finance-query library reports HTTP 451 for US retail on `data-api.binance.vision`, but no public Binance doc confirms Iran is geo-blocked on market-data endpoints. |
| **VPN feasibility** | Plausible but untested. If `data-api.binance.vision` is geo-fenced, an exit node in a non-sanctioned country (e.g., DE, SG, JP) could restore access. Not verified from this environment. |
| **Evidence URL** | `https://developers.binance.com/docs/binance-spot-api-docs/rest-api` (rate limits, security types); `https://github.com/binance/binance-spot-api-docs/blob/master/faqs/market_data_only.md` (market-data-only host); `https://cryptofrontnews.com/binance-responds-to-senate-probe-on-iran-sanctions-claims/` (Iran compliance) |
| **Confidence** | Documented (endpoints, rate limits); Unverified assumption (Iran API-level block on market data) |
| **Code evidence** | `app/config/quality.py:25` (keyless base URL: `https://pro-api.coinmarketcap.com/public-api`); `app/market/global_providers.py:106-111` (acquire_cmc_top125); `app/config/quality.py:74-88` (credential discovery) |

---

### 2.2 CoinMarketCap

| Field | Value |
|-------|-------|
| **Access class** | no-account (Keyless Public API) |
| **Account/KYC** | Not required for keyless endpoints. Registration only needed for authenticated plans. |
| **Endpoint access vs website** | Keyless endpoints available at `pro-api.coinmarketcap.com/public-api` for a curated subset (~35+ routes). Same JSON envelope as Pro API. No headers, no auth. |
| **Free tier & limits** | Keyless: shared IP-based rate pool, no published numeric limit; expect occasional 429. Free Basic plan: 15,000 monthly credits, 50 req/min. |
| **Iran restriction** | Not found. CMC does not document geofencing for market-data endpoints. Account/trading access restricted for Iran. |
| **VPN feasibility** | Not applicable unless an undocumented restriction exists. |
| **Evidence URL** | `https://coinmarketcap.com/api/documentation/pro-api-reference/keyless-public-api`; `https://coinmarketcap.com/api/resources/coinmarketcap-keyless-public-api-guide-developers-guide/` |
| **Confidence** | Documented (keyless endpoints, rate limits confirmed) |
| **Code evidence** | `app/config/quality.py:25` (keyless base URL); `app/market/global_providers.py:106-111`; `app/config/quality.py:26` (authenticated base URL) |

---

### 2.3 CoinGecko

| Field | Value |
|-------|-------|
| **Access class** | no-account (keyless/demo) |
| **Account/KYC** | Not required. Demo tier requires signup for higher limits. |
| **Endpoint access vs website** | Public market data at `https://api.coingecko.com/api/v3/coins/markets`. No API key sent in request (per code: `app/config/quality.py:90-94` reads CG_API_KEY but does not use it). |
| **Free tier & limits** | Keyless: ~10–30 calls/min shared IP-based. Demo plan: 100 calls/min. Paid plans: 300–2,500/min. |
| **Iran restriction** | Not found. No documented API-level geofencing for Iran. |
| **VPN feasibility** | Not applicable unless restriction exists. |
| **Evidence URL** | `https://docs.coingecko.com/docs/keyless-public-api`; `https://www.coingecko.com/en/api/pricing`; `https://support.coingecko.com/hc/en-us/articles/4538771776153` |
| **Confidence** | Documented (endpoints, rate limits confirmed) |
| **Code evidence** | `app/config/quality.py:27` (base URL); `app/market/global_providers.py:150-159` (acquire_coingecko_top125); `app/config/quality.py:90-94` (CG_API_KEY read but unused) |

---

### 2.4 OKX

| Field | Value |
|-------|-------|
| **Access class** | no-account (public REST, no key) |
| **Account/KYC** | Not required for market data endpoints. |
| **Endpoint access vs website** | Public market data at `https://www.okx.com/api/v5/market/history-candles` and `/api/v5/market/books`. No auth for public channels. |
| **Free tier & limits** | Public endpoints: 20 req/2s per IP; overall 600 req/5s. Error 50011 on rate-limit breach. |
| **Iran restriction** | **Documented** — OKX Risk & Compliance Disclosure explicitly lists Iran among Restricted Locations. Applies to services generally; API-level enforcement likely applies. |
| **VPN feasibility** | **Plausible** — exit node in an allowed country (e.g., DE, JP, SG) may restore access. ProxyHat-style residential proxy targeting used by others for similar exchanges. Not verified from this environment. |
| **Evidence URL** | `https://www.okx.com/help/risk-compliance-disclosure`; `https://www.okx.com/docs-v5/en/` (rate limits) |
| **Confidence** | Documented (Iran in restricted locations confirmed) |
| **Code evidence** | `app/config/exchanges.py:84` (OHLCV URL: `https://www.okx.com/api/v5/market/history-candles`); `app/config/exchanges.py:83` (symbol: BTC-USDT) |

---

### 2.5 Bybit

| Field | Value |
|-------|-------|
| **Access class** | no-account (public market data, no key) |
| **Account/KYC** | Not required for market data. Public endpoints under `/v5/market/*` called with no auth headers. |
| **Endpoint access vs website** | Public market data at `https://api.bybit.com/v5/market/kline` and `/v5/market/orderbook`. Separate from account/trading endpoints. |
| **Free tier & limits** | 600 req/5s per IP; HTTP 403 on rate-limit breach (with JSON `retCode` envelope); ~10-minute ban. Error 10009 = "Service Restricted: Access is currently unavailable for your region." |
| **Iran restriction** | **Documented** — Bybit Service Restricted Countries page explicitly lists Iran among Excluded Jurisdictions. API returns 403 for US IPs; "Service Restricted" (error 10009) covers region-based blocking. |
| **VPN feasibility** | **Plausible** — ProxyHat documentation confirms residential proxies geo-targeted to allowed countries (e.g., DE, JP) bypass Bybit geo-blocks. Not verified from this environment. |
| **Evidence URL** | `https://bybit-exchange.github.io/docs/v5/guide` (IP restrictions: US, China); `https://www.bybit.com/en/help-center/article/Service-Restricted-Countries` (Iran in excluded jurisdictions); `https://proxyhat.com/blog/scrape-bybit-v5-market-api-rotating-proxies` (VPN approach) |
| **Confidence** | Documented (Iran explicitly excluded) |
| **Code evidence** | `app/config/exchanges.py:94` (OHLCV URL: `https://api.bybit.com/v5/market/kline`); `app/config/exchanges.py:93` (symbol: BTCUSDT) |

---

### 2.6 KuCoin

| Field | Value |
|-------|-------|
| **Access class** | no-account (public, no key) |
| **Account/KYC** | Not required for public market data. |
| **Endpoint access vs website** | Public endpoints at `https://api.kucoin.com/api/v1/market/candles` (Global) or `https://api.kucoin.eu` (EU). |
| **Free tier & limits** | Public rate-limit pool: 2,000 req/30s per IP. HTTP 429 with code 429000 on breach. Weight 3 for klines endpoint. |
| **Iran restriction** | Not found. No documented API-level geofencing for Iran. |
| **VPN feasibility** | Not applicable unless restriction exists. |
| **Evidence URL** | `https://www.kucoin.com/docs-new/rest/spot-trading/market-data/get-klines`; `https://www.kucoin.com/docs-new/rate-limit-rule-classic` |
| **Confidence** | Documented (endpoints, rate limits confirmed) |
| **Code evidence** | `app/config/exchanges.py:105` (OHLCV URL: `https://api.kucoin.com/api/v1/market/candles`); `app/config/exchanges.py:104` (symbol: BTC-USDT) |

---

### 2.7 Coinbase

| Field | Value |
|-------|-------|
| **Access class** | no-account (public, no key) |
| **Account/KYC** | Not required for public market data on either Pro API or Advanced Trade API. |
| **Endpoint access vs website** | Two public hosts: Pro API at `https://api.exchange.coinbase.com` (used by code at `app/config/exchanges.py:115,183`); Advanced Trade at `https://api.coinbase.com`. Public market data needs no auth on either. |
| **Free tier & limits** | Pro API public: 10 req/sec per IP. Advanced Trade API public: 30 req/sec per IP. HTTP 429 on breach. |
| **Iran restriction** | Not found at API level. Coinbase restricts Iranian accounts for trading/compliance, but no documented API-level geofencing for public market data. |
| **VPN feasibility** | Not applicable unless restriction exists. |
| **Evidence URL** | `https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/public/get-public-product-candles`; `https://docs.cdp.coinbase.com/exchange/introduction/rate-limits-overview` |
| **Confidence** | Documented (rate limits confirmed; Iran API restriction not found) |
| **Code evidence** | `app/config/exchanges.py:115` (OHLCV URL: `https://api.exchange.coinbase.com/products/BTC-USDT/candles`); `app/config/exchanges.py:183` (orderbook URL: `https://api.exchange.coinbase.com/products/BTC-USDT/book`) |

---

### 2.8 Gate

| Field | Value |
|-------|-------|
| **Access class** | no-account (public, no key) |
| **Account/KYC** | Not required for public market data. |
| **Endpoint access vs website** | Public endpoints at `https://api.gateio.ws/api/v4/spot/candlesticks` and `/spot/order_book`. |
| **Free tier & limits** | Public endpoints: 200 req/10s per IP per endpoint (after Jan 2024 adjustment). HTTP 429 on breach. |
| **Iran restriction** | Not found. No documented API-level geofencing for Iran. |
| **VPN feasibility** | Not applicable unless restriction exists. |
| **Evidence URL** | `https://www.gate.com/docs/developers/apiv4/`; `https://www.gate.com/announcements/article/33995` (rate limit adjustment) |
| **Confidence** | Documented (rate limits confirmed) |
| **Code evidence** | `app/config/exchanges.py:123` (OHLCV URL: `https://api.gateio.ws/api/v4/spot/candlesticks`); `app/config/exchanges.py:189` (orderbook URL) |

---

### 2.9 Upbit

| Field | Value |
|-------|-------|
| **Access class** | no-account (public quotation API, no key) |
| **Account/KYC** | Not required for public market data. Quotation endpoints accessible without auth. |
| **Endpoint access vs website** | Regional hosts: KR `https://api.upbit.com`, SG `https://sg-api.upbit.com`, ID `https://id-api.upbit.com`, TH `https://th-api.upbit.com`. Used by code: `app/config/exchanges.py:133,195` (default: `api.upbit.com`). |
| **Free tier & limits** | 10 req/sec per IP per rate-limit group (candle, orderbook, ticker, etc.). HTTP 429 on breach; HTTP 418 if 429 repeated. |
| **Iran restriction** | **Not verified / not found** at API level. Upbit is Korea-focused (KRW markets). Recent policy (Sep 2026): blocking IPs from FATF "gray list" countries — but Iran not explicitly named. Symbol format (USDT-BTC reversed) and KRW-centric design make it a poor fit for BTCUSDT reference pricing. |
| **VPN feasibility** | Plausible — regional endpoints (SG/ID/TH) may allow routing. Not verified. |
| **Evidence URL** | `https://global-docs.upbit.com/reference/api-overview`; `https://docs.upbit.com/kr/reference/rate-limits`; `https://github.com/api-evangelist/upbit` (regional endpoints) |
| **Confidence** | Documented (rate limits, regional endpoints); Unknown (Iran API-level status) |
| **Code evidence** | `app/config/exchanges.py:133` (OHLCV URL: `https://api.upbit.com/v1/candles/minutes/5`); `app/config/exchanges.py:132` (symbol: USDT-BTC); `app/config/exchanges.py:195` (orderbook URL) |

---

### 2.10 Bitget

| Field | Value |
|-------|-------|
| **Access class** | no-account (public, no key) |
| **Account/KYC** | Not required for public market data. |
| **Endpoint access vs website** | Public endpoints at `https://api.bitget.com/api/v2/spot/market/history-candles` and `/api/v2/spot/market/orderbook`. |
| **Free tier & limits** | Public market data: 20 req/sec per IP; overall 6,000 req/min per IP. HTTP 429 on breach. |
| **Iran restriction** | Not found. No documented API-level geofencing for Iran. |
| **VPN feasibility** | Not applicable unless restriction exists. |
| **Evidence URL** | `https://www.bitget.com/docs/uta/rest-api`; `https://www.bitget.com/api-doc/common/faq` |
| **Confidence** | Documented (rate limits confirmed) |
| **Code evidence** | `app/config/exchanges.py:142` (OHLCV URL: `https://api.bitget.com/api/v2/spot/market/history-candles`); `app/config/exchanges.py:141` (symbol: BTCUSDT); `app/config/exchanges.py:199` (orderbook URL) |

---

### 2.11 TradingView (FORBIDDEN in code)

| Field | Value |
|-------|-------|
| **Access class** | registration (keyless not possible for historical) |
| **Account/KYC** | Required. Session cookie (`sessionid`, `sessionid_sign`) needed for real-time/historical bars beyond 5,000. No official market-data API exists. |
| **Endpoint access vs website** | No official market-data API. Endpoints are reverse-engineered WebSocket at `data.tradingview.com`. Anonymous access returns delayed data. |
| **Free tier & limits** | 5,000 bars per fetch for Basic (free) plan. Higher tiers: Plus 10,000, Premium 20,000, Ultimate 40,000. |
| **Iran restriction** | Not found / Not documented. |
| **VPN feasibility** | Unknown. |
| **Evidence URL** | `https://pkg.go.dev/github.com/vmorsell/tradingview-sdk-go/chart`; `https://pypi.org/project/tvkit/0.14.0/`; `https://trdamarker.com/tradingview-api/` |
| **Confidence** | Documented (no official API, reverse-engineered endpoints) |
| **Code evidence** | `FORBIDDEN_RUNTIME_PROVIDERS = {"tradingview", "tradingview_reference", "tv"}` at `app/config/exchanges.py:60-63`; import assert in `app/config/quality.py:63`; runtime check in `app/market/finalization.py:1572-1575` |

---

### 2.12 Independent Aggregators

#### CoinGlass

| Field | Value |
|-------|-------|
| **Access class** | paid (API key required for all endpoints) |
| **Account/KYC** | Registration required. Free plan: 10,000 calls/month (real-time market data only, no historical). Paid: Hobbyist $29/mo (30 req/min), up to Professional $699/mo. |
| **Endpoint access vs website** | All endpoints require API key. No anonymous access. |
| **Free tier & limits** | Free plan: 10,000 calls/month, real-time only. Rate limit varies by paid plan; Hobbyist 30 req/min. |
| **Iran restriction** | Not found / Not documented at API level. |
| **VPN feasibility** | Not applicable (account-based, not IP-restricted). |
| **Evidence URL** | `https://www.coinglass.com/pricing`; `https://docs.coinglass.com/` |
| **Confidence** | Documented (pricing, plans confirmed) |

#### CryptoQuant

| Field | Value |
|-------|-------|
| **Access class** | paid (subscription required) |
| **Account/KYC** | No free tier. API access requires Professional or Premium subscription. Bearer token (`Authorization: Bearer {access_token}`) or `api_key` query param required for all requests. |
| **Endpoint access vs website** | Base URL: `https://api.cryptoquant.com/v1/`. All endpoints require authentication. |
| **Free tier & limits** | None. Professional or Premium subscription required. Rate limits per plan; HTTP 429 on breach. Rate limits separate from API credits. |
| **Iran restriction** | Not found / Not documented at API level. |
| **VPN feasibility** | Not applicable (account-based). |
| **Evidence URL** | `https://docs.cryptoquant.com/guides/quickstart`; `https://docs.cryptoquant.com/guides/faq`; `https://cryptoquant.com/pricing` |
| **Confidence** | Documented (subscription required confirmed) |

#### CryptoCompare

| Field | Value |
|-------|-------|
| **Access class** | registration (free signup was retired May 2026) |
| **Account/KYC** | Free account/signup required since 2026-05-21. API key required for all requests (HTTP 401 without key). Key managed via developer dashboard. |
| **Endpoint access vs website** | Hosts: `min-api.cryptocompare.com` and `data-api.cryptocompare.com`. All require API key. |
| **Free tier & limits** | No keyless tier. Free registered account: limited calls/month (exact number not published). Attribution required in app. |
| **Iran restriction** | Not found / Not documented at API level. |
| **VPN feasibility** | Not applicable (account-based). |
| **Evidence URL** | `https://www.cryptocompare.com/coins/guides/how-to-use-our-api/`; `https://apis.io/security/cryptocompare/cryptocompare-authentication/` |
| **Confidence** | Documented (free tier retired, key required confirmed) |

#### CoinPaprika

| Field | Value |
|-------|-------|
| **Access class** | no-account (free tier, no key) |
| **Account/KYC** | Not required for free tier. |
| **Endpoint access vs website** | Base URL: `https://api.coinpaprika.com/v1/`. Most endpoints work without key. |
| **Free tier & limits** | Free: 20,000 requests/month, 10 req/sec per IP. HTTP 429/402 on breach. Paid plans: Starter 400K, Pro 1M, Business 5M, Ultimate 10M, Enterprise custom. Commercial use allowed in paid plans only. |
| **Iran restriction** | Not found / Not documented at API level. |
| **VPN feasibility** | Not applicable unless undocumented restriction exists. |
| **Evidence URL** | `https://docs.coinpaprika.com/faq`; `https://docs.coinpaprika.com/api-reference/rest-api/introduction` |
| **Confidence** | Documented (rate limits, free tier confirmed) |

---

## 3. Practical Implications

### Best automatic paths (Priority 1)

1. **Binance public market data** (`data-api.binance.vision`) — no key, but **Iran status NOT VERIFIED** at endpoint level. If accessible, it is the fastest option (sub-100ms latency, high rate limits). Code already targets `api.binance.com` (`exchanges.py:74`), not the market-data-only host.
2. **CoinMarketCap keyless** (`/public-api` prefix) — no key, no signup. Code already uses this (`quality.py:25`, `global_providers.py:106-111`). Shared IP rate pool; expect intermittent 429. Migration to free Basic key (15K credits/mo) is trivial.
3. **CoinGecko demo/keyless** — no key. Code already uses this (`quality.py:27`, `global_providers.py:150-159`). ~10–30 calls/min shared limit; register Demo key for 100/min.
4. **Bybit / OKX / KuCoin / Coinbase / Gate / Bitget / CoinPaprika** — all offer public market-data endpoints with no key. Not currently used in code (only Binance OHLCV in the 8-exchange set).

### Conditional paths (Priority 2/3)

5. **Bybit + OKX via VPN** — both **documented** as excluding Iran for services. If the server IP is in an excluded region (or Iranian), a residential proxy or VPN exit node in a non-excluded country (e.g., DE, SG, JP) is the only path. Plausible but **NOT VERIFIED** from this environment.
6. **CMC Basic / CG Demo key** — one-time free registration yields higher rate limits. Bot then runs automatically.
7. **CryptoCompare** — signup now required (free tier retired May 2026). Free key still available, but requires a one-time account.

### Not primary (Priority 4)

8. **CoinGlass** — $29/mo minimum. No anonymous tier. Not a primary solution.
9. **CryptoQuant** — Subscription (Professional/Premium) required. No free tier. Not a primary solution.
10. **TradingView** — FORBIDDEN in code (`exchanges.py:60-63`). No official market-data API. Reverse-engineered endpoints only.

### Unknown from this environment

- No live API probe was performed from the deployment server. The code configures the endpoints, but whether they resolve and return valid data from the server's IP/region is UNKNOWN.
- Whether Binance, CMC, or CoinGecko market-data endpoints are geo-blocked for the server's IP is NOT VERIFIED.
- `CMC_API_KEY` and `CG_API_KEY` runtime environment values are UNKNOWN (code discovery logic exists at `quality.py:74-88, 90-94` but env vars were not inspected).

---

## 4. Key Findings

1. **7 of 10 codebase sources offer truly keyless public access** (Binance, CMC keyless, CoinGecko, Bybit*, OKX*, KuCoin, Coinbase, Gate, Bitget). Upbit is region-specific; CoinPaprika (not in code) also works keyless.

2. **Binance, Bybit, and OKX are documented as restricting Iran** (either explicitly listed or covered by broad compliance policies). Whether this extends to public market-data endpoints specifically (vs. account/trading) is **NOT VERIFIED** — the distinction between website/account restrictions and API endpoint access is not explicitly documented by these providers.

3. **Only 2 independent aggregators investigated as potential supplements** (CoinGlass, CryptoQuant) — both require paid subscriptions. CryptoCompare requires free registration. CoinPaprika offers a viable free keyless tier but is not in the current codebase.

4. **TradingView is explicitly forbidden** in the codebase (`FORBIDDEN_RUNTIME_PROVIDERS`), and has no official market-data API — reverse-engineered endpoints only.

5. **Upbit is poorly suited** for this use case: symbol format is `USDT-BTC` (reversed), markets are KRW-centric, and the exchange is Korea-focused.

6. **The 7-of-8 exchange gate** (`exchange_evidence.py:356-357`, `MIN_VALIDATED_EXCHANGE_COUNT=7` at `exchanges.py:19`) means up to 1 exchange can fail. If 2 exchanges are geo-blocked (e.g., Bybit + OKX for Iran), the gate fails — **this is a critical design risk** for Iran-based deployment.

---

## 5. Evidence Classification Legend

| Label | Meaning |
|-------|---------|
| **Documented** | Claim backed by provider's official documentation (URL cited) |
| **Code evidence** | Claim backed by source code/config in this repository (file:line cited) |
| **Verified** | Claim confirmed by live test from this environment |
| **Unverified assumption** | Claim inferred from documentation but not tested |
| **Not found / Not documented** | No evidence of restriction or feature in provider docs |
| **NOT VERIFIED** | Insufficient evidence to confirm or deny |

---

## 6. Metadata

| Field | Value |
|-------|-------|
| Addendum File | `U06_5_RESEARCH_UNIT_01_ACCESS_ADDENDUM.md` |
| Supplements | `U06_5_RESEARCH_UNIT_01_SOURCES_ACCESS.md` |
| Cell ID | U06.5 |
| Version | 8.4.5 |
| Schema | U06_5_SCHEMA_V6_0 |
| Date | 2026-09-26T14:28:00Z |
| Code modified | NO |
| Live API tested from server | NO |
| Web searches performed | Yes (external docs only — no account creation, KYC, or credential use) |
| Scope excluded | Historical data depth, reliability formulas, ranking/fallback design, Stage 7–12 logic |
