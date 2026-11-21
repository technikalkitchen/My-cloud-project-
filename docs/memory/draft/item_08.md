# draft item_08 — پیش‌نویس تأییدنشده، قاعده نیست
Source: docs/B_items/Item_08_Data_Contract.md (289 خط) | Extracted: 2026-11-21 | وضعیت سند: APPROVED (v1.0، ۱۱ نوامبر ۲۰۲۶)

## ادعاهای سند (به ترتیب بخش‌ها)
- [§0] هدف: تعریف قرارداد داده استاندارد B→C؛ In scope: Data State vocabulary, Candle Schema, Provenance Metadata, Price Path Taxonomy, Supply structure, B→C JSON interface
- [§0] Out of scope: Ranking/Dominance/Coverage (Items 25-27)، Rate limit (Item_09)، Cache (Item_11)، SQLite NOT NULL (Item_12 v2.2)
- [§1] ۵ وضعیت: FULL, PARTIAL, UNAVAILABLE, N_A, PENDING
- [§1] UNAVAILABLE ≠ N_A (اولی تست شد نیست، دومی تست شد بی‌معنی)
- [§1] PARTIAL باید coverage_ratio (0.0-1.0) و missing_ranges داشته باشد
- [§1] PENDING موقت است
- [§1] presence_status (Item_03 §8) = FULL/PARTIAL/UNAVAILABLE؛ N_A و PENDING مخصوص Item_08
- [§2] فیلدهای Identity: asset_id, cmc_id, coingecko_id, symbol, available_from, listing_dates, policy_date, is_stablecoin, is_wrapped, migration
- [§2] cmc_id canonical از CMC top 150 (نه final_125_supply)
- [§2] available_from = CMC data limit، نه actual launch
- [§2] listing_dates = actual exchange listing (Appendix A)
- [§2] policy_date فقط بک‌گراند، در UI نمایش داده نمی‌شود
- [§2] schema_version: "1.0" در هر JSON
- [§3.1] Raw formats per exchange: Binance 12 fields ms/int/str/asc، OKX 9 ms/str/str/desc، Coinbase 6 s/int/num/desc، Bitstamp 6 s/str/str/asc، Crypto.com 6 ms/int/str/asc، Bybit 7 ms/str/str/desc
- [§3.2] Canonical Candle: timestamp_ms int ms، open/high/low/close/volume str، exchange، quote، direction
- [§3.3] Gotchas: Coinbase field order [ts,LOW,HIGH,OPEN,close,vol]، Coinbase price float→Decimal(str(x))، ۴ timestamp format، Direction mix (۳ asc, ۳ desc)، Extra fields نادیده
- [§4.1] Price Path Taxonomy: Direct_USDT, Direct_BTC, Direct_USD_Converted, Implied, N_A
- [§4.2] Provenance Object: quote, price_path, source_exchange, source_pair, conversion_rate_used, rate_source, rate_effective_time, timestamp_ms, fetched_at, validation_status
- [§4.3] Effective Start: direct_start, converted_start=max(usd_start,usdt_usd_start), effective_min=min(direct,converted), imprecise=true اگر walk-back به max_iter یا count_at_start >=182
- [§5] Supply Structure: Dict keyed by asset_id، Daily candles sorted ascending، Coverage 117/125 (۷ NO_DATA + USD1 PENDING)، PROVISIONAL
- [§6] Aggregate: MC(a,d)=supply×price، Dominance=MC/Total_MC، Kitchen Price=Σ(w_i×p_i)/Σw_i
- [§7] B→C Interface: universe.json, prices.json, supply.json, ohlcv.json؛ هر فایل generated_at + schema_version "1.0"؛ Package C فایل با version ناشناخته → reject
- [§8] Boundaries جدول: Data state vocabulary ✅، Candle raw format ✅، Canonical candle ✅، Price path ✅، Provenance ✅، Supply ✅، Aggregate formulas ✅؛ SQLite NOT NULL/Rate limit/Cache خارج
- [§9] Open Questions: ۷ NO_DATA cmc_id ✅ RESOLVED، KMNO ✅ RESOLVED، Coinbase BTC-USDT start ✅ RESOLVED، RNDR dual date ✅ RESOLVED، 币安人生 ⏳ OPEN (P2)، Appendix B available_from ✅ RESOLVED
- [§10] MVP-First: JSON only، ISO 8601 Z در JSON/Unix ms در SQLite، String price در B→C، Provenance صریح، Version هر فایل؛ بدون Backward compat/Schema registry/Field-level encryption/Streaming

## سؤال‌های باز و TODOهای خود سند
- 币安人生 (rank 82) verification pending (P2 Extractor) — فعلاً در Universe

## تکیه بر تصمیم/Item دیگر
- Item_03 (presence_status)، Item_05 (price path)، Item_15 (supply)، Item_16 (OHLCV)، Item_18 (provenance)، Item_12 (SQLite)، Item_09 (rate limit)، Item_11 (cache)، Item_25/29 (MC/Dominance)

## چک کامل بودن
بخش‌های سند: 11 (Section 0-10) | در خلاصه: 11 | ردشده با دلیل: هیچ
EOF