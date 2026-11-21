# item_08
Source: docs/B_items/Item_08_Data_Contract.md (289 خط) | Synced: 2026-11-21 | Status: NEEDS_REWORK

## قواعد معتبر
- ۵ وضعیت داده: FULL, PARTIAL, UNAVAILABLE, N_A, PENDING (Section 1)
- PARTIAL باید coverage_ratio (0.0-1.0) و missing_ranges داشته باشد (Section 1)
- cmc_id canonical از CMC top 150 (Section 2)
- available_from = CMC data limit، نه actual launch (Section 2)
- price_path: Direct_USDT, Direct_BTC, Direct_USD_Converted, Implied, N_A (Section 4.1)
- effective_min = min(direct, converted)؛ imprecise اگر walk-back به max_iter (Section 4.3)
- Package B ۴ فایل تحویل می‌دهد: universe.json, prices.json, supply.json, ohlcv.json (Section 7)
- هر فایل schema_version: "1.0" + generated_at (Section 7)

## قرار است عوض شود
- ۷ NO_DATA cmc_id (SPX, XPL, ...) وضعیت PENDING (Section 9)
- 币安人生 (rank 82) verification pending (Section 9)
- وضعیت سند APPROVED ولی OPEN questions باقی است

## ارتباط با Itemهای دیگر
Item_03 (presence_status), Item_05 (price path), Item_15 (supply), Item_16 (OHLCV), Item_18 (provenance)
EOF