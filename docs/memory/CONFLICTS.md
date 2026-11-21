# CONFLICTS — فهرست یکپارچه‌ی تناقض‌ها

X-01 | POL effective_at: Item_04 می‌گوید 2024-09-04 (§3) vs TEST_MAP خط 42 می‌گوید 2024-09-03 | تصمیم
X-02 | available_from: Item_08 §2 می‌گوید CMC data limit vs CIN-03 (WORK_STATE_OLD) می‌گوید max(exchange_start, listing_date) در Item_13 | تصمیم
X-03 | Item_05: Amendment 4 تغییر PENDING است (Item_05_Canonical_Pairs.md خط 1: PENDING) vs سند اصلی LOCKED (v1.0) | خلأ
X-04 | Dual-Binance: Item_01 §2.2 O-5 باز vs MAP.md v1.1 LOCKED (فهرست ۵ صرافی) | تصمیم
X-05 | Item_06 status PROPOSED vs Item_08 status APPROVED (تناقض در میزان قطعیت) | تصمیم
X-06 | Wrapped Coins: Item_03 §5 می‌گوید کاملاً حذف شدند vs B-35 اصلی می‌گوید مستقل بودند (Item_03 §13) | تصمیم
X-07 | 30m ذخیره vs on-demand: R-30 در TEST_MAP (PROPOSED) vs Item_06 (هیچ ذکری از 30m) | تست
X-08 | Item_09 C-002 سقف ۳۰۰ کندل OBSERVED vs Coinbase 300 تأیید (Item_08 §3.1) | تأییدنشده
X-09 | Item_11 WebSocket ۵ اتصال همزمان: C-019 OPEN (Item_09 §کاندید) vs Item_11 Part2 §3 (نیاز Stage B) | تست
X-10 | Item_03 Survivorship Bias: پذیرفته vs قدیمی می‌گفت حفظ می‌شود (Item_03 §13) | تصمیم (Owner تأیید کرده)
X-11 | Item_12 WAL ممنوع vs محیط PythonAnywhere NFS (Item_12 Part1 §1) | تست (Stage B)
X-12 | Item_11 GitHub Actions به عنوان Executor: C-011 ASSUMED vs Item_11 Part3 §3 | تست
X-13 | Item_05 §2.1 می‌گوید USDT واحد مظنه برای تمام ۱۲۵ vs R-29 Universe = ۱۲۵ خالص پس از حذف Wrapped | تصمیم (R-30 تصمیم گرفته: Universe ۱۲۵ خالص)
X-14 | Item_01 عدد ۷۰٪ پوشش Binance ثبت شده ولی روش محاسبه نامشخص (C-06) | خلأ
X-15 | Item_04 POL ساپلای: CMC داده خطایی (۷۴M) vs منبع جایگزین (POLTRACK) هنوز تعریف نشده (O-2) | تست
EOF