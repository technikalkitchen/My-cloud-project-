# draft item_01 — پیش‌نویس تأییدنشده، قاعده نیست
Source: docs/B_items/Item_01_Exchanges.md (191 خط) | Extracted: 2026-11-21 | وضعیت سند: NEEDS_OWNER_DECISION

## ادعاهای سند (به ترتیب بخش‌ها)
- [§0] پروژه فقط ۵ صرافی مجاز دارد: Binance, OKX, Bitstamp, Coinbase, Crypto.com
- [§1.1] REST Base URLs: Binance Global data-api.binance.vision, Binance US api.binance.us, OKX okx.com, Bitstamp bitstamp.net, Coinbase api.exchange.coinbase.com, Crypto.com api.crypto.com/exchange/v1
- [§1.1] Binance Global و Binance US یک صرافی منطقی محسوب می‌شوند (اگر Dual-Binance تأیید شود)
- [§1.2] OKX در تست ۸۹ درخواست تاریخی متوالی بدون 429 پاسخ داد
- [§1.2] OKX WS: ۸۹ جفت روی یک اتصال، ۱۳۸۵ پیام در ۶۰ ثانیه
- [§1.2] Coinbase WS: ۱۰۳ جفت، ۹۶۵۹ پیام در ۶۰ ثانیه
- [§2.1] Binance Global از data-api.binance.vision و Binance US از api.binance.us
- [§2.1] Binance Global و Binance US نباید دو صرافی مستقل شمرده شوند
- [§2.2] O-5: Dual-Binance باز ثبت شده (Checkpoint ۲۸ اکتبر)
- [§2.2] تست T-03 برای بررسی تفاوت دو Endpoint مطرح شده
- [§2.2] کد TEST001 فقط Binance Global استفاده کرده؛ ترکیب عملیاتی اثبات نشده
- [§2.3] عدد تقریبی ۷۰٪ پوشش Binance ثبت شده ولی نیازمند تعیین روش محاسبه
- [§3] صرافی‌های خارج از Allowlist: Kraken, Bitfinex, CEX.io, Gemini, Bybit, MEXC, Gate.io, KuCoin, Bitget, HTX, LBank, Bitunix
- [§3] DEXها در محدوده منابع مجاز نیستند
- [§4] تمام قیمت‌ها و OHLCV از ۵ صرافی مجاز تأمین می‌شوند
- [§4] Aggregatorها مجاز به تأمین قیمت صرافی یا OHLCV نیستند
- [§4] CMC Internal API منبع اصلی Supply؛ CoinGecko جایگزین
- [§4] تشخیص Pair از Metadata معتبر همان صرافی
- [§4] Retry نباید باعث انتخاب صرافی خارج از منبع انتخاب‌شده شود
- [§5] مرز مسئولیت‌ها: فهرست صرافی‌ها Item_01، Supply Item_02، Canonical Pair Item_05، Rate Limit Item_09، Error Item_10، Bootstrap Item_13، OHLCV Item_16، قیمت Item_18
- [§6] O-5: تأیید نهایی Dual-Binance
- [§6] C-06: تعریف و اعتبارسنجی ۷۰٪ پوشش Binance
- [§6] اعتبارسنجی Endpoint Binance US در محیط اجرایی
- [§6] ثبت دقیق Endpointهای WebSocket تولیدی در Adapterها
- [§6] تأیید نهایی سیاست عدم استفاده از Backup Exchange
- [§6] تعیین وضعیت مستند دلایل حذف صرافی‌های خارج از Allowlist

## سؤال‌های باز و TODOهای خود سند
- O-5: تأیید نهایی مکانیزم Dual-Binance ( تصمیم Owner)
- C-06: تعریف و اعتبارسنجی عدد ۷۰٪ پوشش Binance (نیاز به تست/تعیین روش)
- اعتبارسنجی Endpoint Binance US در محیط اجرایی پروژه (نیاز به تست)
- ثبت دقیق Endpointهای WebSocket تولیدی در Adapterها (نیاز به تست)
- تأیید نهایی سیاست عدم استفاده از Backup Exchange (تصمیم Owner)
- تعیین وضعیت مستند دلایل حذف صرافی‌های خارج از Allowlist (نیاز به مستندسازی)
- WebSocket exact addresses not yet verified (Section 1.1)

## تکیه بر تصمیم/Item دیگر
- MAP.md v1.1 (LOCKED) برای فهرست صرافی‌ها
- Item_02 (Supply/Aggregator)، Item_05 (Canonical Pair)، Item_09 (Rate Limit)، Item_10 (Error/Retry)، Item_13 (Bootstrap)، Item_16 (OHLCV)، Item_18 (قیمت صرافی)

## چک کامل بودن
بخش‌های سند: 7 (بخش ۰-۶) | در خلاصه: 7 | ردشده با دلیل: هیچ
EOF