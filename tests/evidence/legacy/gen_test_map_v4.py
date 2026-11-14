#!/usr/bin/env python3
"""gen_test_map_v4.py — Item-centric TEST_MAP v4 (header-based parsing)."""
import os, re
from collections import defaultdict

MANIFEST = "docs/MANIFEST.md"
TRIAGE = "tests/evidence/triage.tsv"
PENDING = "tests/evidence/pending.tsv"
OUT = "docs/TEST_MAP_v4.md"

ITEM_NAMES = {
    "01":"Exchanges","02":"Aggregators","03":"Universe","04":"Migration Map",
    "05":"Canonical Pairs","06":"Timeframes","07":"Precision & Time",
    "08":"Data Contract","09":"Rate Limit","10":"Error","11":"Cache",
    "12":"Storage","13":"Bootstrap","14":"Incremental","15":"Supply",
    "16":"OHLCV","17":"Exchange Volume","18":"Exchange Price","19":"Exchange MC",
    "20":"Exchange Reliability","21":"Data Reliability","22":"Exchange Dominance",
    "23":"Kitchen Price","24":"Kitchen Volume","25":"Kitchen MC",
    "26":"Kitchen Coverage","27":"Ranking","28":"Grouping",
    "29":"Kitchen Dominance","30":"Snapshot"}

def parse_manifest():
    files = {}
    smap = {"## §1 —":"T1-core","## §3 —":"T1-driver","## §3b —":"T2",
            "## §4 —":"T4-helper","## §5 —":"T4-obsolete","## §6 —":"T4-output",
            "## §7 —":"T4-archive","## §8 —":"T3-amateur","## §9 —":"real-uncat"}
    current = None; header_cols = None
    with open(MANIFEST) as f:
        for line in f:
            line = line.rstrip("\n")
            for prefix, tier in smap.items():
                if line.startswith(prefix):
                    current = tier; header_cols = None; break
            if line.startswith("## §10") or line.startswith("## §11") or line.startswith("## §0"):
                current = None; header_cols = None; continue
            if current is None or not line.startswith("|"): continue
            if line.startswith("| File |"):
                header_cols = [c.strip() for c in line.split("|")[1:-1]]; continue
            if line.startswith("|---"): continue
            if header_cols is None: continue
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) != len(header_cols): continue
            row = dict(zip(header_cols, parts))
            fname = row.get("File", "").strip()
            if not fname: continue
            files[fname] = {"tier": current, "date": row.get("Date","-"),
                            "description": row.get("Description","-")}
    return files

def load_items():
    m = defaultdict(list); cc = []
    if os.path.exists(TRIAGE):
        for line in open(TRIAGE, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"): continue
            p = line.split("\t")
            if len(p) < 3: continue
            fname, items = p[0], p[2]
            if items == "-": continue
            if items == "all": cc.append(fname); continue
            for it in items.split(","):
                it = it.strip()
                if it in ITEM_NAMES: m[it].append(fname)
    return m, cc

def load_pending():
    m = defaultdict(list)
    if os.path.exists(PENDING):
        for line in open(PENDING, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"): continue
            p = line.split("\t")
            if len(p) < 3: continue
            test, items, pri = p[0], p[1], p[2]
            why = p[3] if len(p) > 3 else ""
            for it in items.split(","):
                it = it.strip()
                if it in ITEM_NAMES: m[it].append({"test": test, "pri": pri, "why": why})
    return m

def get_info(files, fname):
    if fname in files: return files[fname]
    return files.get(re.sub(r"#\d+$", "", fname))

def main():
    files = parse_manifest()
    items_map, cc = load_items()
    pending_map = load_pending()
    with open(OUT, "w", encoding="utf-8") as out:
        out.write("# TEST_MAP_v4.md — Item-Centric Test Registry\n\n")
        out.write("**Generated:** auto from MANIFEST + triage + pending\n")
        out.write("**Regenerate:** `python3 tests/evidence/gen_test_map_v4.py`\n\n")
        out.write("**Complement:** MANIFEST = File→Items · This = Item→Files\n\n---\n\n")
        if cc:
            out.write("## §0 — Cross-Cutting Files\n\n| File | Tier | Date | Description |\n|---|---|---|---|\n")
            for fn in cc:
                info = get_info(files, fn)
                if info: out.write(f"| {fn} | {info['tier']} | {info['date']} | {info['description']} |\n")
            out.write("\n---\n\n")
        for num in sorted(ITEM_NAMES.keys()):
            fnames = items_map.get(num, []); pend = pending_map.get(num, [])
            out.write(f"## Item_{num} — {ITEM_NAMES[num]}\n\n")
            if not fnames and not pend:
                out.write("_هیچ تستی ندارد_\n\n---\n\n"); continue
            by_tier = defaultdict(list)
            for fn in fnames:
                info = get_info(files, fn)
                if info: by_tier[info["tier"]].append((fn, info))
            if by_tier:
                out.write("### Tests\n\n| Tier | File | Date | Description |\n|---|---|---|---|\n")
                for tier in ["T1-core","T1-driver","T2","T3-amateur","T4-helper","T4-obsolete","T4-output","real-uncat"]:
                    for fn, info in sorted(by_tier.get(tier, [])):
                        out.write(f"| {tier} | {fn} | {info['date']} | {info['description']} |\n")
                out.write("\n")
            if pend:
                out.write("### PENDING\n\n| Test | Priority | Why |\n|---|---|---|\n")
                for p in pend: out.write(f"| {p['test']} | {p['pri']} | {p['why']} |\n")
                out.write("\n")
            out.write("---\n\n")
        wt = sum(1 for n in ITEM_NAMES if items_map.get(n))
        nt = sum(1 for n in ITEM_NAMES if not items_map.get(n))
        ta = sum(len(v) for v in items_map.values())
        out.write("## §31 — Summary\n\n")
        out.write(f"- **Items with tests:** {wt}/30\n- **Items without tests:** {nt}/30\n")
        out.write(f"- **Total file-assignments:** {ta}\n")
        out.write(f"- **PENDING tests:** {sum(len(v) for v in pending_map.values())}\n")
        out.write(f"- **Cross-cutting:** {len(cc)}\n\n")
        if nt:
            out.write("### Items بدون تست\n\n")
            for n in sorted(ITEM_NAMES):
                if not items_map.get(n): out.write(f"- **Item_{n}** ({ITEM_NAMES[n]})\n")
    print(f"OK: {OUT}")
    print(f"  with_tests: {wt}/30 | without: {nt}/30")
    print(f"  cross_cutting: {len(cc)} | total_assignments: {ta}")

if __name__ == "__main__":
    main()
