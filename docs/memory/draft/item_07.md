# draft item_07 — پیش‌نویس تأییدنشده، قاعده نیست
Source: docs/B_items/Item_07_Precision_Time.md (275 خط) | Extracted: 2026-11-21 | وضعیت سند: APPROVED

## ادعاهای سند (به ترتیب بخش‌ها)
- [§0] Item_07 «قانون» است؛ Item_16 و Item_18 «اجراکننده»
- [§1.1] هیچ عدد حساس (قیمت، ساپلای، حجم، MC) نباید از float عبور کند (B13 §1)
- [§1.1] اعداد غیرحساس: تأخیر شبکه، نسبت‌های تقریبی، Jitter در Backoff
- [§1.2] قیمت‌ها در JSON همیشه String؛ ساپلای String یا Integer؛ حجم String (B13 §2)
- [§1.3] دقت: قیمت USDT ۸ رقم، قیمت BTC ۱۰ رقم، ساپلای ۰-۲ رقم، حجم Base ۸ رقم، حجم Quote ۲ رقم، Dominance ۴ رقم
- [§1.3] دقت ذخیره‌سازی = دقت منبع (نه کمتر، نه بیشتر)
- [§1.4] Coinbase تنها صرافی با قیمت float؛ قانون اجباری: json.loads(response, parse_float=Decimal)
- [§1.4] اثر روی Item_25 (MC): خطای ~1e-15؛ Item_29 (Dominance): مجموع ≠100%؛ Item_27 (Ranking): جابه‌جایی رتبه
- [§2.1] UTC تنها منطقه زمانی مجاز (B12 §1)
- [§2.2] زمان در JSON = ISO 8601 با suffix Z (Item_08 §2)
- [§2.3] ۴ فرمت Timestamp: Binance/Crypto.com ms+int، OKX/Bybit ms+str، Coinbase s+int، Bitstamp s+str
- [§2.3] تبدیل: str→int، s→ms×1000، range check 1230768000000 < ts < 2145916800000
- [§2.3] فقط timestamp_ms (int, ms) در Canonical Candle (Item_08 §3.2)
- [§2.4] Parsing ISO 8601: datetime.fromisoformat(iso_str.replace('Z','+00:00'))؛ ممنوع strptime
- [§2.5] Time-zone Conversion edge case: RESOLVED (A4: همه UTC)
- [§3.1] Rounding: تا زمانی که ممکن است هیچ rounding؛ ROUND_HALF_EVEN (Banker's)
- [§3.1] Rounding فقط در خروجی (UI, MC/Dominance ۴ رقم)
- [§3.2] SQLite storage: قیمت/ساپلای Decimal → TEXT، ساپلای Integer → INTEGER، timestamp → INTEGER ms، volume → TEXT
- [§3.3] DecimalEncoder برای serialization JSON
- [§4] Boundaries: Decimal rule, UTC rule, 4 format timestamp, parse_float=Decimal, ISO 8601 Z, SQLite storage type تعریف؛ Candle format/SQLite impl/Rounding در محاسبات خارج
- [§5] Open Questions: ۱-۳ و ۵ RESOLVED، ۴ DEFERRED (SQLite PRAGMA، Stage B، Item_12)
- [§6] MVP-First: Decimal، parse_float=Decimal، UTC، ISO 8601 Z، 4 format→ms+int، SQLite TEXT/INTEGER، Rounding فقط خروجی
- [§7] Test Requirements: Unit Decimal، Unit Timestamp، Integration Coinbase، Integration SQLite، Regression Aggregation

## سؤال‌های باز و TODOهای خود سند
- SQLite PRAGMA: DEFERRED (Stage B، Item_12)

## تکیه بر تصمیم/Item دیگر
- Item_08 (Data Contract، §2/§3)، Item_16 (OHLCV adapter)، Item_12 (SQLite)، Item_25/29 (MC/Dominance)، Item_27 (Ranking)

## چک کامل بودن
بخش‌های سند: 8 (Section 0-7) | در خلاصه: 8 | ردشده با دلیل: هیچ
EOF