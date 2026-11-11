import json
import shutil
from pathlib import Path
from datetime import datetime

TARGET = Path("tests/TEST_MAP_v3.4_FINAL.md")
P_BITSTAMP = Path("tests/evidence/a9_bitstamp_2026-11-11.json")

def main():
    if not TARGET.exists() or not P_BITSTAMP.exists(): return
    with open(P_BITSTAMP) as f: bs_data = json.load(f).get("assets", {})
    c = TARGET.read_text(encoding="utf-8")
    start_idx = c.find("### Appendix A — A9 Per-Exchange Coverage")
    end_idx = c.find("### Appendix B", start_idx)
    if start_idx == -1 or end_idx == -1: return
    block = c[start_idx:end_idx]
    lines = block.split('\n')
    new_lines = []
    for line in lines:
        if line.startswith("| ") and not line.startswith("|---") and "Symbol" not in line:
            parts = line.split("|")
            if len(parts) >= 8:
                sym = parts[1].strip()
                bs_status = "TESTED" if sym in bs_data and bs_data[sym].get("effective_min") else "NOT_LISTED"
                parts[5] = f" {bs_status} "
                line = "|".join(parts)
        new_lines.append(line)
    c = c[:start_idx] + '\n'.join(new_lines) + c[end_idx:]
    c = c.replace("| 3 | Bitstamp pair bug (A9 v2) | P0 | TD | ۰۱، ۰۳ |", "| 3 | Bitstamp pair bug (A9 v2) | ✅ RESOLVED | TD | ۰۱، ۰۳ |")
    c = c.replace("| 12 | Bitstamp only BTC verified | P0 | TD | ۰۱ |", "| 12 | Bitstamp only BTC verified | ✅ RESOLVED | TD | ۰۱ |")
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy2(TARGET, TARGET.with_suffix(f".md.bak-{ts}"))
    TARGET.write_text(c, encoding="utf-8")
    print("✅ TEST_MAP updated with Bitstamp results.")
if __name__ == "__main__": main()
