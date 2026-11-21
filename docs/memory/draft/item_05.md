# draft item_05 — پیش‌نویس تأییدنشده، قاعده نیست
Source: docs/B_items/Item_05_Canonical_Pairs.md (201 خط) | Extracted: 2026-11-21 | وضعیت سند: LOCKED (v1.0، ۲۷ اکتبر ۲۰۲۶) + PENDING Amendments

## ادعاهای سند (به ترتیب بخش‌ها)
- [§1.1] Direct: فقط اگر صرافی خودش XXX/USDT یا XXX/BTC ارائه کند
- [§1.2] Implied: فقط اگر ورودی‌ها از همان صرافی و زمان مرجع یکسان باشند (SOL/BTC = SOL/USDT ÷ BTC/USDT)
- [§1.3] Fiat Conversion: XXX/USD → XXX/USDT = P(XXX/USD)/P(USDT/USD)؛ منشأ converted_fiat
- [§1.3] rate_effective_time (نه rate_registration_time) معیار زمان است
- [§1.4] قیمت یک صرافی نباید جایگزین قیمت مفقود در صرافی دیگر شود
- [§1.4] نرخ تبدیل از صرافی دیگر مجوز جایگزینی قیمت دارایی نیست
- [§1.5] محاسبات تاریخی از قیمت‌ها و نرخ‌های معتبر در زمان تاریخی (نه فعلی)
- [§1.6] فراداده و منشأ داده باید ثبت شود؛ هماهنگ با Item_08
- [§2.1] USDT واحد مظنه اصلی برای تمام ۱۲۵ دارایی Universe
- [§2.2] BTC واحد مظنه ثانویه برای تمام آلت‌کوین‌ها
- [§2.3] جفت استاندارد BTC = BTC/USDT؛ BTC/BTC = N_A
- [§2.4] اگر صرافی BTC/USDT نداشت، فرض خودکار Fiat Conversion ممنوع؛ UNAVAILABLE اگر نرخ معتبر نباشد
- [§3.1] واحدهای مظنه غیراستاندارد: USD, EUR, JPY, TRY (ورودی تبدیل مجاز)
- [§3.2] فرض برابری USD و USDT ممنوع (P(USDT/USD)≠1)
- [§3.3] P(XXX/USDT) = P(XXX/USD) / P(USDT/USD)
- [§3.4] USDC و DAI نباید برابر ۱ USD فرض شوند؛ قیمت واقعی استفاده شود
- [§3.5] استفاده از نرخ آینده ممنوع؛ نزدیک‌ترین نرخ معتبر قبلی مجاز
- [§3.5] اگر نرخ معتبر در محدوده مجاز نباشد → UNAVAILABLE
- [§3.6] قانون اولویت درون‌صرافی: اگر XXX/USD از صرافی X، نرخ USDT/USD هم از همان صرافی X
- [§3.6] منابع جایگزین فقط اگر صرافی مبدأ USDT/USD نداشت
- [§3.7] فراداده الزامی: conversion_rate_used, rate_source, rate_effective_time, rate_registration_time, input_pair, input_exchange, validation_status
- [§4] پارامترهای Stage B: زمان مرجع کندل، تلورانس، حداکثر عمر نرخ قبلی، ترتیب اولویت منابع، الزامات اعتبارسنجی
- [§5] وابستگی‌ها: Item_01, 03, 04, 08, 09, 10, 16 (ورودی)؛ Item_16, 18, 23, 25, 29, 30 (مصرف‌کننده)
- [Pending Amd 1] چهار دسته: Direct_USDT, Direct_BTC, Direct_USD_Converted, Implied (استیبل/فیات دیگر)
- [Pending Amd 1] نام قدیمی Converted_fiat → Direct_USD_Converted
- [Pending Amd 2] ترتیب اولویت: USDT → BTC → USD → USDC/DAI → فیات دیگر؛ اگر USDT هست هرگز USDC
- [Pending Amd 3] دامنه فقط کریپتو-محور؛ فیات به فیات خارج
- [Pending Amd 4] همه Market Cap به USDT نمایش داده می‌شوند (mockup USD→USDT)

## سؤال‌های باز و TODOهای خود سند
- Stage B: زمان مرجع کندل، تلورانس، حداکثر عمر نرخ قبلی، ترتیب اولویت منابع، الزامات اعتبارسنجی (§4)
- Amendmentها PENDING — در انتظار Amendment واحد پس از تست‌ها

## تکیه بر تصمیم/Item دیگر
- Item_01 (صرافی‌ها)، Item_03 (Universe)، Item_04 (Migration Map)، Item_08 (Data Contract)، Item_09 (Rate Limit)، Item_10 (Error)، Item_16 (OHLCV)، Item_18 (قیمت)، Item_23 (Kitchen Price)، Item_25 (MC)، Item_29 (Dominance)، Item_30 (Snapshot)

## چک کامل بودن
بخش‌های سند: 6 (بخش ۱-۵ + Pending Amendments ۴ تغییر) | در خلاصه: 6 | ردشده با دلیل: هیچ
EOF