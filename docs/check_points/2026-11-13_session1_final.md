═══════════════════════════════════════════════════════════════
CHECKPOINT FINAL v4 — TD-02 + AM-03 | سشن ۲ | ۱۳ نوامبر ۲۰۲۶
═══════════════════════════════════════════════════════════════

از: TD-02 (📐) + AM-03 (🧭)
به: Patcher (Termux) → Owner
نسخه: FINAL v4 — ساده (R-30 و Item_06 به فاز بازنویسی موکول)
وضعیت: AM-03 CONFIRMED + TD-02 CONFIRMED — منتظر Owner APPROVE

───────────────────────────────────────────────────────────────
§0 — Version Rule
───────────────────────────────────────────────────────────────

| وضعیت | فایل |
|---|---|
| معتبر (تست‌ها) | docs/MANIFEST.md |
| مرجع دانش (R-Laws) | docs/B_items/Cross_Item_Notes.md |
| مرجع scope آیتم‌ها | docs/MAP.md |
| Archive | TEST_MAP v3.4_FINAL · v3.4.4_preview · v3.4.2_appendices · v2.1 · *.bak |

───────────────────────────────────────────────────────────────
§1 — ماجرا (خلاصه برای AM-03)
───────────────────────────────────────────────────────────────

مشکل Owner (سه بار تکرار): «فایل‌های تست پراکنده، هیچ دستیاری نمی‌فهمد کدام تست
به کدام آیتم می‌خورد، چطور تضمین می‌کنی چیزی جا نیفتد؟»

سه شکست پیش از این:
  v1 (AM-03): CURATED dict دستی، Summary از حافظه
  v2: auto-summary ضعیف
  v3: KeyError 'T1'

راه‌حل v4: خودکار از repo + دستی فقط ۲ ستون (Item + Tier override) + Validation Gate.

───────────────────────────────────────────────────────────────
§2 — وضعیت نهایی MANIFEST (تأییدشده)
───────────────────────────────────────────────────────────────

  Total files:   133
  PENDING:       5
  Sum check:     133 = 133 (assert پاس)

  §1  T1-Core:       20   (شاهد قطعی، Item دارد)
  §3  T1-Driver:     13   (اسکریپت‌های تولید شواهد — Item = `—`، GAP شناخته‌شده)
  §3b T2-Caveat:     17   (rate_limit ۲۹–۳۰ Oct با caveat)
  §4  T4-Helper:     25   (patch/fix/TEST001 infra)
  §5  T4-Obsolete:   15   (.github workflows)
  §6  T4-Output:     35   (results/run_*/)
  §8  T3-Amateur:     7   (coverage/legacy ۲۸–۳۰ Oct)
  §9  Real-Uncat:     1   (__init__.py — package marker)
  §10 PENDING:        5
  ─────────────────────────
  جمع فایل‌ها:      133 ✅

سه باگ که امروز حل شد:
  - Duplicate: final_125_supply.json ×۲ → یکی + #2
  - PENDING format: ستون چسبیده → ۴ ستون جدا
  - TEST001: adapters.py/config.py/runner.py در T1 → §4

───────────────────────────────────────────────────────────────
§3 — فایل‌های تولیدشده
───────────────────────────────────────────────────────────────

| فایل | نقش | commit |
|---|---|---|
| docs/MANIFEST.md (۲۰۳ خط) | منبع خودکفای تست‌ها | 92bb6e7 + patch |
| docs/TEAM_PROTOCOL.md (بخش ۱۰) | Amendment MANIFEST workflow | 92bb6e7 |
| tests/evidence/scan_repo.sh | لیست فایل‌ها از repo | 92bb6e7 |
| tests/evidence/gen_manifest.py | بازسازی MANIFEST | 92bb6e7 + patch |
| tests/evidence/triage.tsv | tier override + items (دستی) | 92bb6e7 |
| tests/evidence/pending.tsv | تست‌های نگرفته (دستی) | 92bb6e7 |

───────────────────────────────────────────────────────────────
§4 — Amendment §10 (تأییدشده)
───────────────────────────────────────────────────────────────

قاعده طلایی: «هر دستیار جدید → اول MANIFEST. اگر Summary کافی بود، فایل تست باز نمی‌شود.»

چرخه تست جدید (اجباری — R-25):
  ۱. bash tests/evidence/scan_repo.sh
  ۲. یک خط به tests/evidence/triage.tsv: filename<TAB>tier<TAB>items<TAB>note
  ۳. python3 tests/evidence/gen_manifest.py
  ۴. Commit با test(evidence): <name> — Item_XX

Validation Gate: اگر assert sum(sections) == len(rows) شکست خورد → کامیت ممنوع.

───────────────────────────────────────────────────────────────
§5 — کشفیات جدید این سشن
───────────────────────────────────────────────────────────────

| فایل | کشف | اثر |
|---|---|---|
| a9_coinbase_2026-11-11.json | usdt_usd_start=2021-05-04، ۹۹/۱۵۰ | P1 حل شد (Item_08 §9 #3) |
| 7_no_data_resolved_2026-11-11.json | همه ۷ new asset، ۲۰۱۷ ندارد | P2 حل شد (Item_08 §9 #1) |
| a9_bitstamp_2026-11-11.json | ۸۵/۱۵۰ (جایگزین v2 با ۱/۱۵۰) | Item_01 و 03 |
| A6/2026-11-07_migration_extract.md | extract مهاجرت | Item_04 |
| test_map_audit_2026-11-13.txt | باگ دارد (بخش commit خالی) | در §9 Real-Uncat |

از ۶ PENDING v3.4، ۲ مورد امروز حل شد — با شاهد قطعی.

───────────────────────────────────────────────────────────────
§6 — ۵ PENDING واقعی
───────────────────────────────────────────────────────────────

| Test | Item | P | Why |
|---|---|---|---|
| Bitstamp candle cap | 01,09 | P0 | سقف ۳۰۰ تأیید نشده |
| Coinbase REST rate | 09 | P0 | GAP — هرگز تست نشد |
| C-019b (۵-conn WS) | 09,11 | P0 | R-03 تصویب، تست نشده |
| WS Binance/Bybit | 11 | P1 | Part 2 v1.5 PROVISIONAL |
| USD1 DefiLlama | 15 | P3 | کم‌اولویت |

───────────────────────────────────────────────────────────────
§7 — آیتم‌های آماده بازنویسی
───────────────────────────────────────────────────────────────

| # | Item | وضعیت | P |
|---|---|---|---|
| Item_08 v1.1 | P1+P2 امروز حل شد — تناقض ساختاری مانده | آماده ✅ | P0 |
| Item_05 §1.3 | ۴ Amendment ۳۰ Oct اعمال نشده | آماده ✅ | P0 |
| Item_09 v11.0 | تست‌های حرفه‌ای غایب (C-019, Bybit, Bitstamp cap) | آماده ✅ | P1 |
| Item_01 v1.1 | Bybit غایب (R-11) + ۶ OPEN | آماده ✅ | P1 |
| Item_06 Part 1 | نوشته نشده — منتظر فاز بازنویسی. R-30 و ۳vs۴ TF به آن فاز موکول. | — | — |

───────────────────────────────────────────────────────────────
§8 — ۲۰ آیتم نانوشته
───────────────────────────────────────────────────────────────

| # | Item | Tests در MANIFEST | تست لازم نیست |
|---|---|---|---|
| 02 | Aggregators | CMC cap=732 | CoinGecko/DefiLlama/CoinMetrics (P2) |
| 12 | Storage | A5 (13.17MB) | — |
| 13 | Bootstrap | A1, A3, a9_coinbase_11 | BLOCKED (placeholder) |
| 14 | Incremental | A1 (غیرمستقیم) | تست اختصاصی ندارد |
| 15 | Supply | A5, final_125, 7_no_data_resolved | USD1 (P3), KMNO patch |
| 16 | OHLCV | A4 (کامل) | — |
| 17 | Exch Volume | A4 (فیلد v) | تست اختصاصی ندارد |
| 18 | Exch Price | A9 OKX v3.2, Binance/Bybit/Bitstamp v2 | A9 v3 BTC (P1) |
| 19–30 | Package B Core | A5/A9/R-29/derived | unit formula (همراه نوشتن) |

───────────────────────────────────────────────────────────────
§9 — تأیید و یادداشت AM-03 + TD-02
───────────────────────────────────────────────────────────────

چک‌لیست:
[x] تأیید ۲۰ فایل T1-Core
[x] تأیید ۱۳ فایل T1-Driver (Item = `—`، GAP شناخته‌شده — نه مشکل)
[x] تأیید ۵ PENDING
[x] تأیید Amendment §10
[x] تأیید commit 92bb6e7 + patch
[x] تأیید ۲ PENDING حل‌شده (۷ NO_DATA + Coinbase BTC-USDT date)

یادداشت AM-03:
چک‌پوینت v4 را کامل تأیید می‌کنم. Manifest امروز کار ما بود و تمام شد.
R-30 و ۳vs۴ TF و Item_06 به فاز بازنویسی موکول شدند — امروز کار ما نیستند.

یادداشت TD-02:
تصحیح AM-03 پذیرفته شد. سادگی بهتر از پیچیدگی. R-30 امروز کار ما نیست.
Manifest امروز بسته شد — آماده برای شروع Item_08 v1.1.

تاریخ/ساعت: ۱۳ نوامبر ۲۰۲۶ | ۱۹:۴۰ Tehran
تأیید AM-03: CONFIRMED
تأیید TD-02: CONFIRMED
تأیید Owner: _______

───────────────────────────────────────────────────────────────
§10 — دستورات Patcher (آماده — بدون placeholder)
───────────────────────────────────────────────────────────────

دستور ۱ — بررسی وضعیت:
  cd /workspaces/My-cloud-project-
  git log -1 --oneline
  git status

دستور ۲ — ذخیره چک‌پوینت:
  متن این پیام (§0 تا §12) را در فایل زیر ذخیره کن
  (با nano یا heredoc — محتوای واقعی، بدون placeholder):
  docs/check_points/2026-11-13_session2_final.md

دستور ۳ — commit چک‌پوینت:
  git add docs/check_points/2026-11-13_session2_final.md
  git commit -m "docs(checkpoint): session 2 final v4 — MANIFEST 133 files + AM/TD CONFIRMED"

دستور ۴ — push:
  git push
  git log --oneline -3

───────────────────────────────────────────────────────────────
§11 — مسیر بعدی (پس از push)
───────────────────────────────────────────────────────────────

ترتیب بازنویسی:
  ۱. Item_08 v1.1 (P0) — P1+P2 حل شد، فقط تناقض ساختاری
  ۲. Item_05 §1.3 (P0) — ۴ Amendment ۳۰ Oct
  ۳. Item_09 v11.0 (P1) — تست‌های حرفه‌ای
  ۴. Item_01 v1.1 (P1) — Bybit + ۶ OPEN
  ۵. Item_06 Part 1 — وقتی رسیدیم، R-30 را حل می‌کنیم

قاعده حاکم: هر ادعا از MANIFEST — نه از حافظه.

───────────────────────────────────────────────────────────────
§12 — Commit History این سشن
───────────────────────────────────────────────────────────────

  92bb6e7  feat(manifest): self-sufficient registry — 133 files, 5 pending, Amendment §10
  <next>   docs(checkpoint): session 2 final v4 — AM/TD CONFIRMED

═══════════════════════════════════════════════════════════════
End of CHECKPOINT FINAL v4 — TD-02 + AM-03 | سشن ۲ | ۱۳ Nov 2026
═══════════════════════════════════════════════════════════════
