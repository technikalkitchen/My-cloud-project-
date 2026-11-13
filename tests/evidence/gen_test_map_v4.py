#!/usr/bin/env python3
"""gen_test_map_v4.py — Item-centric TEST_MAP v4 from MANIFEST + triage."""
import os, re
from collections import defaultdict

MANIFEST = "docs/MANIFEST.md"
TRIAGE = "tests/evidence/triage.tsv"
PENDING = "tests/evidence/pending.tsv"
OUT = "docs/TEST_MAP_v4.md"

ITEM_NAMES = {
    "01": "Exchanges", "02": "Aggregators", "03": "Universe",
    "04": "Migration Map", "05": "Canonical Pairs", "06": "Timeframes",
    "07": "Precision & Time", "08": "Data Contract", "09": "Rate Limit",
    "10": "Error", "11": "Cache", "12": "Storage", "13": "Bootstrap",
    "14": "Incremental", "15": "Supply", "16": "OHLCV",
    "17": "Exchange Volume", "18": "Exchange Price", "19": "Exchange MC",
    "20": "Exchange Reliability", "21": "Data Reliability", "22": "Exchange Dominance",
    "23": "Kitchen Price", "24": "Kitchen Volume", "25": "Kitchen MC",
    "26": "Kitchen Coverage", "27": "Ranking", "28": "Grouping",
    "29": "Kitchen Dominance", "30": "Snapshot"
}

files = {}
section_map = {
    "## §1 —": "T1-core", "## §3 —": "T1-driver", "## §3b —": "T2",
    "## §4 —": "T4-helper", "## §5 —": "T4-obsolete", "## §6 —": "T4-output",
    "## §8 —": "T3-amateur", "## §9 —": "real-uncat"
}
current = None
with open(MANIFEST) as f:
    for line in f:
        for prefix, tier in section_map.items():
            if line.startswith(prefix):
                current = tier
                break
        if line.startswith("## §10") or line.startswith("## §0"):
            current = None
        if current and line.startswith("|") and not line.startswith("|---") and "File" not in line:
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 3 and parts[0]:
                fname = parts[0]
                if current in ("T1-core", "T1-driver") and len(parts) >= 4:
                    files[fname] = {"tier": current, "date": parts[2], "summary": parts[3]}
                elif len(parts) >= 3:
                    files[fname] = {"tier": current, "date": parts[1], "summary": parts[2]}

items_map = defaultdict(list)
cross_cutting = []
with open(TRIAGE) as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        p = line.rstrip("\n").split("\t")
        if len(p) < 3: continue
        fname, tier, items = p[0], p[1], p[2]
        if items == "-": continue
        if items == "all":
            cross_cutting.append(fname); continue
        for item in items.split(","):
            item = item.strip()
            if item in ITEM_NAMES:
                items_map[item].append(fname)

pending_map = defaultdict(list)
with open(PENDING) as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        p = line.rstrip("\n").split("\t")
        if len(p) < 3: continue
        test, items, pri = p[0], p[1], p[2]
        why = p[3] if len(p) > 3 else ""
        for item in items.split(","):
            item = item.strip()
            if item in ITEM_NAMES:
                pending_map[item].append({"test": test, "pri": pri, "why": why})

def get_info(fname):
    if fname in files: return files[fname]
    return files.get(re.sub(r"#\d+$", "", fname))

with open(OUT, "w", encoding="utf-8") as out:
    out.write("# TEST_MAP_v4.md — Item-Centric Test Registry\n\n")
    out.write("**Generated:** auto from `docs/MANIFEST.md` + `tests/evidence/triage.tsv` + `pending.tsv`\n")
    out.write("**Regenerate:** `python3 tests/evidence/gen_test_map_v4.py`\n\n")
    out.write("**Complement:** `docs/MANIFEST.md` = File → Items · This file = Item → Files\n\n---\n\n")
    
    if cross_cutting:
        out.write("## §0 — Cross-Cutting Files (apply to all items)\n\n")
        out.write("| File | Tier | Date | Summary |\n|---|---|---|---|\n")
        for fname in cross_cutting:
            info = get_info(fname)
            if info:
                out.write(f"| {fname} | {info['tier']} | {info['date']} | {info['summary']} |\n")
        out.write("\n---\n\n")
    
    for num in sorted(ITEM_NAMES.keys()):
        fnames = items_map.get(num, [])
        pend = pending_map.get(num, [])
        out.write(f"## Item_{num} — {ITEM_NAMES[num]}\n\n")
        if not fnames and not pend:
            out.write("_هیچ تستی ندارد_\n\n---\n\n"); continue
        by_tier = defaultdict(list)
        for fname in fnames:
            info = get_info(fname)
            if info: by_tier[info["tier"]].append((fname, info))
        if by_tier:
            out.write("### Tests\n\n")
            out.write("| Tier | File | Date | Summary |\n|---|---|---|---|\n")
            for tier in ["T1-core", "T1-driver", "T2", "T3-amateur", "T4-helper", "T4-obsolete", "T4-output", "real-uncat"]:
                for fname, info in sorted(by_tier.get(tier, [])):
                    out.write(f"| {tier} | {fname} | {info['date']} | {info['summary']} |\n")
            out.write("\n")
        if pend:
            out.write("### PENDING\n\n| Test | Priority | Why |\n|---|---|---|\n")
            for p in pend:
                out.write(f"| {p['test']} | {p['pri']} | {p['why']} |\n")
            out.write("\n")
        out.write("---\n\n")
    
    with_tests = sum(1 for n in ITEM_NAMES if items_map.get(n))
    no_tests = sum(1 for n in ITEM_NAMES if not items_map.get(n))
    total_assignments = sum(len(v) for v in items_map.values())
    out.write("## §31 — Summary\n\n")
    out.write(f"- **Items with tests:** {with_tests}/30\n")
    out.write(f"- **Items without tests:** {no_tests}/30\n")
    out.write(f"- **Total file-assignments:** {total_assignments}\n")
    out.write(f"- **PENDING tests:** {sum(len(v) for v in pending_map.values())}\n")
    out.write(f"- **Cross-cutting:** {len(cross_cutting)}\n\n")
    if no_tests:
        out.write("### Items بدون تست\n\n")
        for n in sorted(ITEM_NAMES):
            if not items_map.get(n):
                out.write(f"- **Item_{n}** ({ITEM_NAMES[n]})\n")

print(f"OK: {OUT}")
print(f"  with_tests: {with_tests}/30 | without: {no_tests}/30")
print(f"  cross_cutting: {len(cross_cutting)} | total_assignments: {total_assignments}")
