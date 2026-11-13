#!/usr/bin/env python3
"""gen_manifest.py — Auto-summary + triage + pending. Manual: فقط tier override + items."""
import os, json, re, datetime

RAW = "tests/evidence/raw_tests.tsv"
TRIAGE = "tests/evidence/triage.tsv"
PENDING = "tests/evidence/pending.tsv"
OUT = "docs/MANIFEST.md"

META = {"gen_manifest.py", "gen_manifest_v2.py", "gen_manifest_v3.py",
        "gen_manifest_v4.py", "triage.tsv", "items.tsv", "pending.tsv",
        "raw_tests.tsv", "scan_repo.sh"}

def load_tsv(path, default=None):
    m = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"): continue
            parts = line.split("\t")
            if len(parts) >= 3:
                m[parts[0]] = {
                    "tier": parts[1] if parts[1] != "-" else None,
                    "items": parts[2] if parts[2] != "-" else "—",
                    "note": parts[3] if len(parts) >= 4 and parts[3] != "-" else None,
                }
    return m

def load_pending():
    m = []
    if os.path.exists(PENDING):
        for line in open(PENDING, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"): continue
            m.append(line.split("\t"))
    return m

def auto_tier(path):
    if path.startswith(".github/workflows/"): return "T4-obsolete"
    if path.startswith("results/"):          return "T4-output"
    if path.startswith("tests/coverage/") or path.startswith("tests/legacy_test001/"):
        return "T3-amateur"
    if ".bak-" in path or path.endswith(".bak"): return "T4-archive"
    if path.startswith("tests/stages/"):     return "T4-obsolete"
    if path.startswith("tests/evidence/scripts/"):
        fn = path.lower()
        PATCH = ("patch","fix_","update_tmap","migrate_archive","park_legacy",
                 "clean_legacy","final_clean","create_item_registry",
                 "force_park","r07_patch","remove_junk","validate_tmap",
                 "verify_test_map","generate_appendices")
        if any(k in fn for k in PATCH): return "T4-helper"
        return "T1-driver"
    if path.startswith("tests/evidence/scripts/"): return "T4-helper"
    return None  # از in_tm/items بعداً

def auto_summary(path):
    try:
        if path.endswith(".json"):
            d = json.load(open(path, encoding="utf-8"))
            if isinstance(d, dict):
                parts = []
                for k, v in list(d.items())[:8]:
                    if isinstance(v, bool): parts.append(f"{k}={v}")
                    elif isinstance(v, (int, float)): parts.append(f"{k}={v}")
                    elif isinstance(v, str):
                        sv = v if len(v) <= 40 else v[:40] + "…"
                        parts.append(f"{k}={sv}")
                    elif isinstance(v, dict): parts.append(f"{k}{{{len(v)}}}")
                    elif isinstance(v, list): parts.append(f"{k}[{len(v)}]")
                return " · ".join(parts[:6]) if parts else "(empty dict)"
            return f"list[{len(d)}]"
        if path.endswith((".md", ".txt")):
            txt = open(path, encoding="utf-8", errors="ignore").read()
            if len(txt) < 500:
                return " ".join(txt.split())[:300]
            for para in txt.split("\n\n"):
                p = para.strip()
                if p and not p.startswith("#"):
                    return " ".join(p.split())[:200]
        if path.endswith(".py"):
            c = open(path, encoding="utf-8", errors="ignore").read()
            m = re.search(r'"""(.*?)"""', c, re.DOTALL)
            if m: return m.group(1).strip().split("\n")[0][:200]
            m = re.search(r"^#\s*(.+)$", c, re.MULTILINE)
            if m: return m.group(1)[:200]
    except Exception as e:
        return f"(err:{type(e).__name__})"
    return "—"

def main():
    triage = load_tsv(TRIAGE)
    pending = load_pending()
    rows = []
    with open(RAW, encoding="utf-8") as f:
        for line in f:
            if line.startswith(("#", "path\t", "filename\t")): continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 5: continue
            path, fname, date, size, in_tm = parts[:5]
            if fname in META: continue
            t = triage.get(fname, {})
            tier = t.get("tier") or auto_tier(path)
            if tier is None:
                if in_tm == "YES": tier = "T1-core"
                elif t.get("items", "—") != "—": tier = "T1-post"
                else: tier = "real-uncat"
            summary = t.get("note") or auto_summary(path)
            rows.append({"fname": fname, "path": path, "date": date, "size": size,
                         "in_tm": in_tm, "items": t.get("items", "—"),
                         "tier": tier, "summary": summary})

    TIER_MAP = {"T1": "T1-core", "T2": "T2-caveat", "T3": "T3-amateur"}
    for r in rows:
        r["tier"] = TIER_MAP.get(r["tier"], r["tier"])
    groups = {k: [] for k in ["T1-core","T1-post","T1-driver","T2-caveat",
                              "T4-helper","T4-obsolete","T4-output","T4-archive",
                              "T3-amateur","real-uncat"]}
    for r in rows: groups[r["tier"]].append(r)
    total = sum(len(g) for g in groups.values())
    assert total == len(rows), f"gap: {total} != {len(rows)}"

    titles = {
        "T1-core":   "§1 — T1-Core: In TEST_MAP (شاهد قطعی)",
        "T1-post":   "§2 — T1-Post: Post-TEST_MAP Discoveries",
        "T1-driver": "§3 — T1-Driver Scripts (تولیدکننده شواهد)",
        "T2-caveat": "§3b — T2: Active with Reconfirm (rate_limit ۲۹–۳۰ Oct)",
        "T4-helper": "§4 — T4 Helper Scripts",
        "T4-obsolete":"§5 — T4 Obsolete Workflows",
        "T4-output": "§6 — T4 Test Outputs",
        "T4-archive":"§7 — T4 Archived Versions",
        "T3-amateur":"§8 — T3 Amateur Period",
        "real-uncat":"§9 — Real Uncategorized",
    }

    with open(OUT, "w", encoding="utf-8") as out:
        now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        out.write(f"# MANIFEST.md — Self-Sufficient Test Registry\n\n")
        out.write(f"**Generated:** {now}\n")
        out.write(f"**Total files:** {total} | **PENDING (هنوز نگرفته):** {len(pending)}\n\n")
        out.write("**Regenerate:** `bash tests/evidence/scan_repo.sh && python3 tests/evidence/gen_manifest.py`\n")
        out.write("**Manual edits فقط:** `triage.tsv` (tier/items) + `pending.tsv` (تست‌های نگرفته)\n\n")

        out.write("## §0 — Version Rule\n\n")
        out.write("| وضعیت | فایل |\n|---|---|\n")
        out.write("| **معتبر (تست‌ها)** | این فایل (MANIFEST.md) |\n")
        out.write("| **مرجع دانش (R-Laws)** | docs/B_items/Cross_Item_Notes.md |\n")
        out.write("| **مرجع scope آیتم‌ها** | docs/MAP.md |\n")
        out.write("| **بازنویسی R-Laws** | Cross_Item_Notes (R-01..R-32) |\n")
        out.write("| Archive | v3.4_FINAL · v3.4.4_preview · v3.4.2_appendices · v2.1 · *.bak |\n\n")

        for key, title in titles.items():
            g = groups[key]
            if not g and key != "real-uncat": continue
            out.write(f"\n## {title} ({len(g)} فایل)\n\n")
            if key == "real-uncat" and not g:
                out.write("_هیچ فایلی بدون طبقه‌بندی نیست_ ✅\n")
                continue
            if key.startswith("T1"):
                out.write("| File | Item | Date | Summary |\n|---|---|---|---|\n")
                for r in sorted(g, key=lambda x: x["fname"]):
                    out.write(f"| {r['fname']} | {r['items']} | {r['date']} | {r['summary']} |\n")
            else:
                out.write("| File | Date | Summary |\n|---|---|---|\n")
                for r in sorted(g, key=lambda x: x["fname"]):
                    out.write(f"| {r['fname']} | {r['date']} | {r['summary'][:120]} |\n")

        # §10 PENDING
        out.write(f"\n## §10 — PENDING Tests (هنوز گرفته نشده) ({len(pending)})\n\n")
        if pending:
            out.write("| Test | Item | P | Why |\n|---|---|---|---|\n")
            for row in pending:
                row += [""] * (4 - len(row))
                out.write(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} |\n")
        else:
            out.write("_همه تست‌ها گرفته شده_ ✅\n")

    print(f"OK: total={total} | rows={len(rows)} | pending={len(pending)}")
    for k in groups:
        if groups[k]: print(f"  {k}: {len(groups[k])}")

if __name__ == "__main__":
    main()
