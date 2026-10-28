# B_Items_List.md — ایندکس Legacy

**پروژه:** Kitchen Assistant Bot V4
**تاریخ:** ۲۸ اکتبر ۲۰۲۶ | ۱۹:۰۰ تهران
**نسخه:** ۲.۰

---

## هدف این فایل

ایندکس رسمی آیتم‌های Legacy پروژه. این فایل فهرست کامل Legacyهای طراحی‌شده در تاریخچه را نگه می‌دارد. محتوای طراحی‌ها در فایل‌های `B_legacy/BXX_Master.md` ذخیره شده‌اند (۱۹ فایل موجود) یا در آینده نوشته خواهند شد (۴۲ فایل باقی‌مانده).

**توجه:** Legacy ها مرجع تاریخی هستند. طراحی‌های جدید در `B_items/` انجام می‌شوند.

---

## دسته ۱ — زیرساخت پایه (۱۷ ردیف)

1. B-01 (صرافی‌ها) — ✅
2. B-02 (Aggregatorها) — ✅
3. B-03 (Pair Canonical) — ✅
4. B-04 (Direct vs Implied) — ✅
5. B-05 (Timeframe System — شامل B-06 و B-09) — ✅
6. B-07 (OHLCV) — ✅
7. B-08 (Volume) — ✅
8. B-10 (Order Book — موکول به فاز ۳) — ✅ (در `B10_B11_Master`)
9. B-11 (Trades — حذف‌شده) — ✅ (در `B10_B11_Master`)
10. B-12 (Timezone) — ✅
11. B-13 (Data Precision) — ✅
12. B-15 (Error Handling) — ✅
13. B-17 (Current Ranking) — ✅ (در `B17_B18_Master`)
14. B-18 (Historical Ranking) — ✅ (در `B17_B18_Master`)
15. B-35, B-36, B-37 (Universe, Groups, Priority) — ✅ (در `B35_B36_B37_Master`)
16. B-39, B-40 (Snapshot, RUN_ID) — ✅ (در `B40_B41_Master` — فقط B-40 و B-41؛ B-39 نوشته نشده)
17. B-75 (Custom Range — ادغام در B-05) — ❌

## دسته ۲ — منابع داده و Rate Limit (۳ ردیف)

18. B-14 (Rate Limit — ۵ فایل: `B14_Master_1` تا `B14_Master_5_Decision_LOCKED`) — ✅
19. B-16 (Supply) — ❌
20. B-72 (Per-User Limit — ادغام در B-14) — ❌

## دسته ۳ — لایه میانی محاسباتی (۱۵ ردیف)

21. B-19 (Stablecoin Classification — ادغام در Item 03) — ❌
22. B-20 (Coin Metadata) — ❌
23. B-21 (XXX/BTC Coverage — ادغام در B-04) — ❌
24. B-22 (Cross-Exchange Validation) — ❌
25. B-23 (Kitchen Price — USDT) — ❌
26. B-24 (Kitchen Price — BTC) — ❌
27. B-25 (Implied Weight) — ❌
28. B-26 (Outlier Detection) — ❌
29. B-27 (Kitchen Volume) — ❌
30. B-28 (Kitchen Market Cap) — ❌
31. B-29 (Exchange Market Cap) — ❌
32. B-30 (Exchange Dominance) — ❌
33. B-31 (Kitchen Dominance) — ❌
34. B-32 (Reliability Formula) — ❌
35. B-33 (Fallback Chain) — ❌

## دسته ۴ — اتصالات و Traceability (۱۰ ردیف)

36. B-34 (Exchange Eligibility) — ❌
37. B-38 (Group Assignment Logic) — ❌
38. B-41 (Provenance) — ✅ (در `B40_B41_Master`)
39. B-42 (Price Source Labeling) — ❌
40. B-43 (Data Status) — ❌
41. B-44 (Dominance Metadata) — ❌
42. B-45 (Snapshot Frequency) — ❌
43. B-46 (B→C Data Contract) — ❌
44. B-47 (مرز B↔C) — ❌
45. B-48 (Explicitly Out-of-B) — ❌

## دسته ۵ — ذخیره‌سازی و Collector (۱۱ ردیف)

46. B-49 (Daily Ranking Collector) — ❌
47. B-50 (Storage — Local + Drive) — ❌
48. B-51 (Bootstrap Load) — ❌
49. B-52 (Incremental Update) — ❌
50. B-53 (Cache Strategy) — ❌
51. B-54 (Retention Policy) — ❌
52. B-55 (Volume Weighting over Time) — ❌
53. B-56 (Kitchen Volume Edge Cases) — ❌
54. B-69 (Top 125 Ranking تاریخی — ادغام در B-18) — ❌
55. B-70 (Canonical Data Model — ادغام در B-07/B-08) — ❌
56. B-71 (Reliability Evidence) — ❌

---

## آمار

- **مجموع آیتم‌های Legacy یکتا:** ۶۱ (B-01 تا B-56، B-69 تا B-72، B-75)
- **فایل‌های موجود در `B_legacy/`:** ۱۹
- **Legacy های نوشته‌نشده:** ۴۲
- **Legacy های ادغام‌شده** (بدون فایل مستقل): B-06، B-09، B-19، B-21، B-37، B-70
- **Legacy های غیرموجود:** B-73، B-74 (شماره‌گذاری پرش داشت)
- **B-57 تا B-68:** هرگز طراحی نشدند

---

## توضیح ستون ✅/❌

- ✅ = فایل Legacy نوشته شده و در `B_legacy/` موجود است
- ❌ = Legacy طراحی نشده. طراحی آیتم معادل در `B_items/` انجام می‌شود.

**توجه:** این فایل صرفاً ایندکس است. برای مشاهده محتوای هر Legacy، به فایل `B_legacy/BXX_Master.md` مراجعه کنید.

---

## تغییرات این فایل

| نسخه | تاریخ | تغییرات |
|---|---|---|
| ۱.۰ | ۲۶ اکتبر ۲۰۲۶ | نسخه اولیه |
| ۲.۰ | ۲۸ اکتبر ۲۰۲۶ | اصلاح تعداد کل به ۶۱ (شمارش دقیق). حذف برچسب‌های وضعیت (CLOSED/IN PROGRESS). افزودن ستون فایل موجود. تصحیح شمارش دسته‌ها (دسته ۳ = ۱۵، دسته ۴ = ۱۰، دسته ۵ = ۱۱). |

---

**پایان B_Items_List.md**
