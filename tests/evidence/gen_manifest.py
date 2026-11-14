#!/usr/bin/env python3
"""gen_manifest.py — Auto-summary + triage + pending."""
import os, json, re, datetime

RAW = "tests/evidence/raw_tests.tsv"
TRIAGE = "tests/evidence/triage.tsv"
PENDING = "tests/evidence/pending.tsv"
OUT = "docs/MANIFEST.md"

META = {"gen_manifest.py", "gen_manifest_v2.py", "gen_manifest_v3.py",
        "gen_manifest_v4.py", "triage.tsv", "items.tsv", "pending.tsv",
        "raw_tests.tsv", "scan_repo.sh"}

def load_tsv(path):
    m = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"): continue
            parts = line.split("\t")
            if len(parts) >= 3:
                m[parts[0]] = {
                    "tier": parts[1] if parts[1] != "-" else None,
                    "items": parts[2] if parts[2] != "-" else "-",
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
    if path.startswith("app/market/test001/"): return "T4-helper"
    if path.startswith("tests/evidence/scripts/"):
        fn = path.lower()
        PATCH = ("patch","fix_","update_tmap","migrate_archive","park_legacy",
                 "clean_legacy","final_clean","create_item_registry",
                 "force_park","r07_patch","remove_junk","validate_tmap",
                 "verify_test_map","generate_appendices")
        if any(k in fn for k in PATCH): return "T4-helper"
        return "T1-driver"
    return None

def auto_summary(path):
    try:
        if path.endswith(".json"):
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
            if isinstance(d, dict):
                desc = None
                for key in ("description", "test", "name", "title", "test_name"):
                    if key in d and isinstance(d[key], str) and len(d[key]) < 200:
                        desc = str(d[key])[:100]
                        break
                if not desc:
                    if "usdt_usd_start" in d:
                        desc = f"Coinbase USDT/USD test (from {d['usdt_usd_start']})"
                    elif "resolved_assets" in d and isinstance(d["resolved_assets"], (dict, list)):
                        desc = f"Resolution ({len(d['resolved_assets'])} items)"
                    elif "assets" in d and isinstance(d["assets"], (list, dict)):
                        desc = f"Per-asset scan ({len(d['assets'])} assets)"
                    elif len(d) > 50:
                        desc = f"JSON dict ({len(d)} entries)"
                    else:
                        desc = f"JSON ({', '.join(list(d.keys())[:3])})"
                key_parts = []
                for k, v in list(d.items())[:8]:
                    if isinstance(v, bool):
                        key_parts.append(f"{k}={v}")
                    elif isinstance(v, (int, float)):
                        key_parts.append(f"{k}={v}")
                    elif isinstance(v, str):
                        sv = v if len(v) <= 40 else v[:40] + "..."
                        key_parts.append(f"{k}={sv}")
                    elif isinstance(v, dict):
                        key_parts.append(f"{k}{{{len(v)}}}")
                    elif isinstance(v, list):
                        key_parts.append(f"{k}[{len(v)}]")
                return (desc, " | ".join(key_parts[:6]) if key_parts else "-")
            elif isinstance(d, list):
                return (f"JSON list[{len(d)}]", "-")
            return ("JSON", "-")
        if path.endswith((".md", ".txt")):
            txt = open(path, encoding="utf-8", errors="ignore").read()
            lines = [l.strip() for l in txt.split("\n") if l.strip()]
            desc = "text"
            for line in lines[:20]:
                if line.startswith("#"):
                    desc = line.lstrip("#").strip()[:100]
                    break
                if not line.startswith("```") and not line.startswith("|"):
                    desc = line[:100]
                    break
            return (desc, "-")
        if path.endswith(".py"):
            c = open(path, encoding="utf-8", errors="ignore").read()
            m = re.search(r'"""(.*?)"""', c, re.DOTALL)
            if m:
                desc = m.group(1).strip().split("\n")[0][:100]
            else:
                m2 = re.search(r"^#\s*(.+)$", c, re.MULTILINE)
                desc = m2.group(1)[:100] if m2 else "Python script"
            return (desc, "-")
    except Exception as e:
        return (f"(err:{type(e).__name__})", "-")
    return ("-", "-")

def main():
    triage = load_tsv(TRIAGE)
    pending = load_pending()
    rows = []
    seen = {}
    with open(RAW, encoding="utf-8") as f:
        for line in f:
            if line.startswith(("#", "path\t", "filename\t")): continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 5: continue
            path, fname, date, size, in_tm = parts[:5]
            if fname in META: continue
            if fname in seen:
                seen[fname] += 1
                fname = fname + "#" + str(seen[fname])
            else:
                seen[fname] = 1
            t = triage.get(fname.split("#")[0], {})
            tier = t.get("tier") or auto_tier(path)
            if tier is None:
                if in_tm == "YES": tier = "T1-core"
                elif t.get("items", "-") != "-": tier = "T1-post"
                else: tier = "real-uncat"
            auto_desc, auto_key = auto_summary(path)
            if tier.startswith("T4"):
                description = f"not a test - {tier.replace('T4-', '')}"
                key_numbers = "-"
            else:
                description = t.get("note") or auto_desc
                key_numbers = auto_key
            rows.append({"fname": fname, "path": path, "date": date,
                         "in_tm": in_tm, "items": t.get("items", "-"),
                         "tier": tier, "description": description,
                         "key_numbers": key_numbers})

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
        "T2-caveat": "§3b — T2: Active with Reconfirm (rate_limit ۲۹-۳۰ Oct)",
        "T4-helper": "§4 — T4 Helper Scripts",
        "T4-obsolete":"§5 — T4 Obsolete Workflows",
        "T4-output": "§6 — T4 Test Outputs",
        "T4-archive":"§7 — T4 Archived Versions",
        "T3-amateur":"§8 — T3 Amateur Period",
        "real-uncat":"§9 — Real Uncategorized",
    }

    with open(OUT, "w", encoding="utf-8") as out:
        now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        out.write("# MANIFEST.md - Self-Sufficient Test Registry\n\n")
        out.write(f"**Generated:** {now}\n")
        out.write(f"**Total files:** {total} | **PENDING:** {len(pending)}\n\n")
        out.write("**Regenerate:** `bash tests/evidence/scan_repo.sh && python3 tests/evidence/gen_manifest.py`\n")
        out.write("**Manual edits:** `triage.tsv` (tier/items) + `pending.tsv`\n\n")
        out.write("## §0 — Version Rule\n\n")
        out.write("| Status | File |\n|---|---|\n")
        out.write("| Valid (tests) | MANIFEST.md (this file) |\n")
        out.write("| Knowledge (R-Laws) | docs/B_items/Cross_Item_Notes.md |\n")
        out.write("| Scope | docs/MAP.md |\n")
        out.write("| Item-Centric view | docs/TEST_MAP_v4.md |\n")
        out.write("| Archive | v3.4_FINAL · *.bak |\n\n")

        for key, title in titles.items():
            g = groups[key]
            if not g and key != "real-uncat": continue
            out.write(f"\n## {title} ({len(g)})\n\n")
            if key == "real-uncat" and not g:
                out.write("_هیچ فایلی بدون طبقه‌بندی نیست_ ✅\n")
                continue
            if key.startswith("T1"):
                out.write("| File | Item | Date | Description | Key Numbers |\n")
                out.write("|---|---|---|---|---|\n")
                for r in sorted(g, key=lambda x: x["fname"]):
                    out.write(f"| {r['fname']} | {r['items']} | {r['date']} | {r['description']} | {r['key_numbers']} |\n")
            else:
                out.write("| File | Date | Description | Key Numbers |\n")
                out.write("|---|---|---|---|\n")
                for r in sorted(g, key=lambda x: x["fname"]):
                    out.write(f"| {r['fname']} | {r['date']} | {r['description'][:100]} | {r['key_numbers'][:100]} |\n")

        out.write(f"\n## §10 — PENDING Tests ({len(pending)})\n\n")
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
