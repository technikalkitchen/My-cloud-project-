#!/usr/bin/env python3
"""
Audit Script — ۱۱ نوامبر ۲۰۲۶
هدف: پاسخ شفاف به ۱۰+۲ سؤال باز (v3.4)
خروجی: tests/evidence/audit_2026-11-11.json + .md
R-12b: در tests/evidence/scripts/ نگه داشته شود
"""
import json
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

REPO = Path(".").resolve()
OUTPUT_JSON = REPO / "tests/evidence/audit_2026-11-11.json"
OUTPUT_MD = REPO / "tests/evidence/audit_2026-11-11.md"

SEVEN_NO_DATA = ["SPX", "XPL", "FF", "PIEVERSE", "KITE", "MON", "NFT"]

def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return {"ok": r.returncode == 0, "out": r.stdout.strip(), "err": r.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {"ok": False, "out": "", "err": "timeout"}
    except Exception as e:
        return {"ok": False, "out": "", "err": str(e)}

def section_a():
    """بدون network — بررسی repo"""
    results = {}

    # A1 — A8 وجود
    r = run(f"find {REPO} -type f \\( -iname '*a8*' -o -iname '*bootstrap*' \\) -not -path '*/.git/*'")
    results["A1_a8_bootstrap"] = {
        "found": r["out"] != "",
        "files": r["out"].split("\n") if r["out"] else []
    }

    # A2 — a9_okx_v3
    r = run(f"find {REPO}/tests/evidence -type f -name '*a9_okx_v3*' 2>/dev/null")
    results["A2_a9_okx_v3"] = {
        "found": r["out"] != "",
        "files": r["out"].split("\n") if r["out"] else []
    }

    # A3 — A6_A7_okx_correction.json
    p = REPO / "tests/evidence/A6_A7_okx_correction_2026-11-09.json"
    if p.exists():
        try:
            data = json.loads(p.read_text())
            results["A3_okx_correction"] = {
                "exists": True,
                "content": data,
                "poly": data.get("POL") or data.get("pol"),
                "render": data.get("RENDER") or data.get("render"),
                "s": data.get("S") or data.get("s")
            }
        except Exception as e:
            results["A3_okx_correction"] = {"exists": True, "parse_error": str(e)}
    else:
        results["A3_okx_correction"] = {"exists": False}

    # A4 — A5 supply_timeseries
    p = REPO / "results/supply_timeseries/supply_timeseries_2026-11-07.json"
    if p.exists():
        size_mb = p.stat().st_size / (1024*1024)
        try:
            data = json.loads(p.read_text())
            count = len(data) if isinstance(data, list) else len(data.get("assets", {}))
            results["A4_a5_timeseries"] = {"exists": True, "size_mb": round(size_mb, 2), "count": count}
        except Exception as e:
            results["A4_a5_timeseries"] = {"exists": True, "size_mb": round(size_mb, 2), "parse_error": str(e)}
    else:
        results["A4_a5_timeseries"] = {"exists": False}

    # A5 — git log A1/A2/A3
    r = run(f"cd {REPO} && git log --all --oneline --grep='A1\\|A2\\|A3\\|OKX\\|supply' -i 2>/dev/null | head -20")
    results["A5_commits"] = {"lines": r["out"].split("\n") if r["out"] else []}

    # A6 — KMNO 32415
    r = run(f"cd {REPO} && grep -rl '32415' --include='*.md' --include='*.json' --include='*.py' --include='*.yml' . 2>/dev/null | grep -v '.git'")
    results["A6_kmno_old_id"] = {"files": r["out"].split("\n") if r["out"] else []}

    # A7 — ۷ NO_DATA در final_125_supply
    p = REPO / "results/final_supply_harvest"
    candidates = list(p.rglob("final_125_supply.json")) if p.exists() else []
    if candidates:
        try:
            data = json.loads(candidates[0].read_text())
            seven = [a for a in data if a.get("symbol") in SEVEN_NO_DATA]
            results["A7_seven_no_data"] = {"found_file": str(candidates[0]), "items": seven}
        except Exception as e:
            results["A7_seven_no_data"] = {"parse_error": str(e), "files": [str(c) for c in candidates]}
    else:
        results["A7_seven_no_data"] = {"exists": False, "searched_in": str(p)}

    # A8 — تناقض cmc_id final vs a9
    p_a9 = REPO / "tests/evidence/a9_okx_2026-11-09.json"
    p_final = candidates[0] if candidates else None
    contradictions = []
    if p_a9.exists() and p_final:
        try:
            a9 = json.loads(p_a9.read_text())
            final = json.loads(p_final.read_text())
            # A9 structure — لیست یا dict
            a9_assets = a9 if isinstance(a9, list) else a9.get("assets", [])
            final_map = {a.get("symbol"): a.get("cmc_id") for a in final}
            for a in a9_assets:
                sym = a.get("symbol")
                a9_id = a.get("cmc_id")
                if sym in final_map and final_map[sym] != a9_id:
                    contradictions.append({"symbol": sym, "final": final_map[sym], "a9": a9_id})
            results["A8_cmc_contradictions"] = contradictions
        except Exception as e:
            results["A8_cmc_contradictions"] = {"parse_error": str(e)}
    else:
        results["A8_cmc_contradictions"] = {"exists": False, "a9": p_a9.exists(), "final": p_final is not None}

    # A9 — pol_bybit
    p = REPO / "tests/evidence/pol_bybit_test_2026-11-08.json"
    if p.exists():
        try:
            data = json.loads(p.read_text())
            results["A9_pol_bybit"] = {"exists": True, "content": data}
        except Exception as e:
            results["A9_pol_bybit"] = {"exists": True, "parse_error": str(e)}
    else:
        results["A9_pol_bybit"] = {"exists": False}

    # A10 — TEST001 قدیمی
    r = run(f"find {REPO} -type f -path '*adapters*' -not -path '*/.git/*' 2>/dev/null")
    results["A10_test001_adapters"] = {"files": r["out"].split("\n") if r["out"] else []}

    return results

def cmc_search(symbol):
    """CMC /search — یک درخواست"""
    url = f"https://api.coinmarketcap.com/data-api/v3/search?keyword={symbol}&limit=5"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            # ساده‌سازی: لیست نتایج
            items = data.get("data", {}).get("crypto", []) or data.get("data", {}).get("list", [])
            return [{"id": it.get("id"), "symbol": it.get("symbol"), "name": it.get("name")} for it in items[:3]]
    except Exception as e:
        return {"error": str(e)}

def section_b():
    """با network — CMC /search"""
    results = {}
    for sym in SEVEN_NO_DATA:
        results[sym] = cmc_search(sym)
        time.sleep(1)  # polite
    return results

def write_outputs(sec_a, sec_b):
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "section_a_repo": sec_a, "section_b_cmc": sec_b}
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2))

    # خلاصه markdown
    md = ["# Audit — ۱۱ نوامبر ۲۰۲۶", "", f"**Generated:** {payload['generated_at']}", ""]
    md.append("## Section A — Repo")
    for k, v in sec_a.items():
        md.append(f"### {k}")
        md.append("```json")
        md.append(json.dumps(v, ensure_ascii=False, indent=2)[:800])
        md.append("```")
        md.append("")

    md.append("## Section B — CMC /search")
    for sym, res in sec_b.items():
        md.append(f"### {sym}")
        md.append("```json")
        md.append(json.dumps(res, ensure_ascii=False, indent=2))
        md.append("```")
        md.append("")

    OUTPUT_MD.write_text("\n".join(md))
    print(f"\n✅ خروجی:\n  {OUTPUT_JSON}\n  {OUTPUT_MD}")

def main():
    print("═══ Audit Script ۱۱ نوامبر ۲۰۲۶ ═══")
    print("Section A — Repo (بدون network)...")
    sec_a = section_a()
    print(f"  ✅ {len(sec_a)} مورد بررسی شد")

    print("\nSection B — CMC /search (۷ درخواست، ~۱۰ ثانیه)...")
    sec_b = section_b()
    print(f"  ✅ {len(sec_b)} مورد بررسی شد")

    write_outputs(sec_a, sec_b)
    print("\n═══ پایان ═══")

if __name__ == "__main__":
    main()
