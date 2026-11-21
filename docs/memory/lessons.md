Source: tests/TEST_MAP_v3.4_FINAL.md | Extracted: 2026-11-21

## قواعد کاری
L-01: [Diagnostic] قبل از اجرای multi-exchange، ۵-۱۰ تست BTC per-exchange بزن (R-26) (Section 5, R-26)
L-02: [Save] اسکریپت‌های >۵ دقیقه باید per-10-asset ذخیره کنند (R-27) (Section 5, R-27)
L-03: [Return type] تغییر return type تابع → همه callerها آپدیت (R-28) (Section 5, R-28)
L-04: [Scripts] اسکریپت‌های تست در tests/evidence/scripts/ نه /tmp (R-12b) (Section 5, R-12b)
L-05: [Large files] فایل‌های >۱۰MB با git add -f (R-12a) (Section 5, R-12a)

## واقعیت‌های داده و صرافی (ممکن است کهنه شود)
آخرین تأیید: 2026-11-21 (از Test Map V3.4)
L-06: [CMC ID] NO_DATA لزوماً «عدم داده در CMC» نیست؛ cmc_id اشتباه ممکن است (Section 2.2.5)
L-07: [Authoritative] A9 cmc_top150 (8 Nov) authoritative است، نه final_125_supply (Section 2.2.5)
L-08: [Coinbase] سقف ۳۰۰ کندل؛ درخواست ۱ ساله → 400؛ pagination لازم (Section 2.5, t6)
L-09: [OHLCV] ۵ ناسازگاری بین صرافی‌ها (field order, timestamp, price type, direction, count) → adapter per-exchange (Section 2.2)
L-10: [TEST001] TEST001 پیش از R-11/A2 است؛ Item_01/06/16 نباید از آن مشتق شوند (Section 2.7)
L-11: [Supply date] available_from = اولین تاریخ داده CMC، نه launch date واقعی (Appendix B)
L-12: [Coinbase scope] فقط USD + USDT quotes؛ BTC-USDC delisted و USDC-USD NOT_FOUND (Section 2.6)
L-13: [KMNO] cmc_id تغییر کرد (32415→30986) — CMC re-listing/symbol collision (Section 10)
L-14: [Bitstamp] فقط BTC verified؛ pair bug حل شد (Section 13, #3)
L-15: [Universe] CMC Top 150 → حذف Wrapped → ۱۲۵ خالص (R-29) (Section 5, R-29)
L-18: [POL Bybit] launchTime=null، pre-migration alias از 2023-10-25 (Section 2.1)
L-19: [MATIC/RNDR/FTM] OKX pair را rename کرده — source NOT_LISTED، فقط target (Appendix D)
L-20: [No commit] A1-A3 اسکریپت در repo ندارند؛ برای بازتولید TD باید بازنویسی کند (R-12b) (Section 2.1)

## کارهای باز (در STATE.md هم بیاید)
L-16: [RNDR] دو تاریخ (effective_at + listing_dates) — تصمیم UI باز (R-32) (Section 5, R-32)
L-17: [USD1] تنها stablecoin بدون داده؛ تست DefiLlama (R-31a) (Section 5, R-31a)
EOF