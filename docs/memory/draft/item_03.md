# draft item_03 — پیش‌نویس تأییدنشده، قاعده نیست
Source: docs/B_items/Item_03_Universe.md (353 خط) | Extracted: 2026-11-21 | وضعیت سند: ✅ CLOSED (TD و Owner، ۲۶ اکتبر ۲۰۲۶)

## ادعاهای سند (به ترتیب بخش‌ها)
- [§1] Current Universe = فهرست فعلی ۱۲۵ دارایی برتر CoinGecko، یک بار در ماه به‌روز
- [§1] Universe Snapshot = نسخه‌ی ثبت‌شده برای بازتولیدپذیری
- [§1] Historical Scan روی Current Universe اجرا می‌شود (نه Snapshot تاریخی)
- [§2] Survivorship Bias پذیرفته: فقط دارایی‌های فعال امروز (FTT, LUNA حذف)
- [§2] پیام Footer در اسکن‌های تاریخی: «این اسکن تاریخی فقط شامل دارایی‌هایی است که امروز فعال هستند...»
- [§2] تعداد واقعی دارایی‌های دارای داده در Runtime محاسبه می‌شود (آیتم ۲۵)
- [§3] asset_id پایدار از CoinGecko ID (نه symbol)
- [§3] Migration (MATIC→POL و...) در آیتم ۴ مدیریت می‌شود
- [§4] Stablecoins در Universe هستند، در Total MC حاضر، در Money Flow ردیف جدا (Stablecoins.D)
- [§4] Stablecoins در هیچ Top 10/5/3 نمایش داده نمی‌شوند (O-7 CLOSED)
- [§4] قاعده جایگزینی (Replacement Logic): Stablecoins حذف و کوین‌های بعدی جایگزین
- [§4] قیمت Stablecoins از بازار گرفته می‌شود (نه ثابت ۱.۰۰)
- [§4] هر Stablecoin یک دارایی است (چندزنجیره‌ای یکجا)
- [§5] Wrapped Coins در Universe نیستند (دلایل: بازار جدا، قیمت متفاوت، دو بار شماری)
- [§5] برای Wrapped Coins ساپلای دریافت نمی‌شود
- [§6] فهرست Stablecoins کنترلی: USDT, USDC, DAI, TUSD, USDP, FDUSD, PYUSD, BUSD
- [§6] قاعده شناسایی: تگ CoinGecko = منبع اولیه؛ فهرست کنترلی = مکمل/override؛ کنترلی برنده در اختلاف (O-2 CLOSED)
- [§7] فهرست Wrapped کنترلی: WBTC, stETH, WETH, wstETH, rETH, cbETH
- [§7] تگ CoinGecko (wrapped) = منبع اولیه؛ کنترلی برنده در اختلاف
- [§8] عضویت در Universe ≠ داده معتبر (presence_status: FULL/PARTIAL/UNAVAILABLE)
- [§8] membership_status: ACTIVE / OUT_OF_TOP_125 / SUPPORT_ASSET / INACTIVE
- [§8] available_from, available_to, presence_status برای هر بازه
- [§8] نبود Supply ≠ نبود داده قیمت (اصلاح TD)
- [§9] پوشش یونیورس در هر صرافی = چند دارایی از ۱۲۵ در آن صرافی داده دارند
- [§10] منبع فهرست ۱۲۵: CoinGecko، endpoint /api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=150 (O-1 CLOSED)
- [§10] Wrapped حذف، ۱۲۵ اول برداشته می‌شود
- [§11] Support Assets: فقط USDT (O-6 CLOSED)
- [§11] اگر USDC از ۱۲۵ خارج شد → از Stablecoins.D هم خارج می‌شود
- [§11] اگر USDT از ۱۲۵ خارج شد → به‌عنوان Support Asset می‌ماند
- [§11] ranked_universe_count + support_asset_count = universe_count
- [§12] Universe ثابت نیست؛ داینامیک Universe ≠ داینامیک Ranking
- [§14] Migration Map به آیتم ۴ منتقل شد (O-5 CLOSED)
- [§15] مرز با Itemهای ۲، ۴، ۵، ۸، ۱۵، ۱۸، ۲۰، ۲۵، ۲۷، ۲۸، ۳۰
- [§16] همه ۷ مورد OPEN (O-1 تا O-7) CLOSED

## سؤال‌های باز و TODOهای خود سند
- هیچ OPEN باقی نمی‌ماند (تمام O-1..O-7 CLOSED)
- دقت تگ‌ها در Stage B تست می‌شود (O-2)
- CoinGecko منبع اصلی، تست در Stage B، escalation اگر <95% (O-3)
- ذخیره فهرست Stablecoins در Metadata یا فایل جدا (تصمیم Stage B)

## تکیه بر تصمیم/Item دیگر
- Item_02 (Aggregator/Supply)، Item_04 (Migration)، Item_05 (Canonical Pair)، Item_08 (Data Contract)، Item_15 (Supply)، Item_18 (قیمت)، Item_20 (اعتبار صرافی)، Item_25 (پوشش کیچن)، Item_27 (رتبه‌بندی)، Item_28 (گروه‌بندی)، Item_30 (اسنپ‌شات)

## چک کامل بودن
بخش‌های سند: 16 (زیرمجموعه ۱-۱۵ + موارد OPEN) | در خلاصه: 16 | ردشده با دلیل: هیچ
EOF