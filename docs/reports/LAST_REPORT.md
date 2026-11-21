تعداد تناقض‌ها: 15 (تصمیم: 7، تست: 5، خلأ: 2، حل‌شده با R-30: 1) | سؤال باز: 30

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
# OPEN_QUESTIONS — سؤال‌های باز و TODOهای اسناد

Q-01 | Dual-Binance تأیید نهایی (O-5) | Item_01 §6
Q-02 | ۷۰٪ پوشش Binance: روش محاسبه و اعتبارسنجی (C-06) | Item_01 §6
Q-03 | Endpoint Binance US در محیط اجرایی اعتبارسنجی | Item_01 §6
Q-04 | Endpointهای WebSocket تولیدی در Adapterها ثبت | Item_01 §6
Q-05 | سیاست عدم استفاده از Backup Exchange تأیید | Item_01 §6
Q-06 | دلایل حذف صرافی‌های خارج از Allowlist مستندسازی | Item_01 §6
Q-07 | Stage B تست تگ‌های CoinGecko (O-2) | Item_03 §6
Q-08 | CoinGecko منبع اصلی، تست Stage B، escalation اگر <95% (O-3) | Item_03 §6
Q-09 | ذخیره فهرست Stablecoins در Metadata یا فایل جدا | Item_03 §6
Q-10 | O-1: الگوریتم انتخاب TF در حالت From beginning (TD, Stage B) | Item_06 §5
Q-11 | Part 2 و Part 3 Item_06 هنوز تعریف نشده | Item_06 §5
Q-12 | SQLite PRAGMA: DEFERRED (Stage B, Item_12) | Item_07 §5
Q-13 | 币安人生 (rank 82) verification (P2 Extractor) | Item_08 §9
Q-14 | C-015 تا C-019 OPEN (Stage B) | Item_09 §کاندید
Q-15 | C-003: سقف واقعی CMC نامشخص | Item_09 §رجیستری
Q-16 | Coinbase 400 pattern (P2, Stage B) | Item_10 §8
Q-17 | Safe Probe endpoint (P2, Item_01 adapter) | Item_10 §8
Q-18 | WebSocket ۵ اتصال همزمان اندازه‌گیری (C-019) | Item_11 Part2 §3
Q-19 | GitHub Actions به عنوان Executor مشروط (C-011) | Item_11 Part3 §3
Q-20 | Reuse Policy برای Completed Job تعریف نشده | Item_11 Part2 §4
Q-21 | Not Listed TTL در Item_16 تعریف شود | Item_11 Part3 §4
Q-22 | File Locking روی NFS (Stage B) | Item_12 Part1 §1
Q-23 | Multi-Dispatcher روی SQLite/NFS تا تأیید Stage B | Item_12 Part1 §1
Q-24 | POL منبع جایگزین (POLTRACK/آن‌چین) و نوع متریک (O-2, TD, Stage B) | Item_04 §7
Q-25 | مهاجرت‌های پیچیده (BTT, LUNA) در فاز ۲ (O-1) | Item_04 §7
Q-26 | قالب نمایش نماد قدیم/جدید در UI (O-3) | Item_04 §7
Q-27 | Amendmentهای Item_05 PENDING (۴ تغییر) | Item_05 Pending
Q-28 | Stage B پارامترهای Fiat Conversion (زمان مرجع، تلورانس، حداکثر عمر نرخ) | Item_05 §4
Q-29 | R-30/R-31a/R-31b/R-32 تصمیم Owner (PROPOSED/OPEN) | TEST_MAP §5
Q-30 | ۷ NO_DATA cmc_id اصلاح (P2 Extractor) | TEST_MAP §2.2.5
EOF