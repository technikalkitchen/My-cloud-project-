#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re
import shutil
from pathlib import Path
from datetime import datetime

TARGET = Path("tests/TEST_MAP_v3.4_FINAL.md")
P_COINBASE = Path("tests/evidence/a9_coinbase_2026-11-11.json")

def main():
    if not TARGET.exists() or not P_COINBASE.exists():
        print("❌ File not found.")
        return

    # 1. Load Coinbase Data
    with open(P_COINBASE) as f:
        cb_data = json.load(f).get("assets", {})

    c = TARGET.read_text(encoding="utf-8")

    # 2. Update Appendix A Coinbase Column
    # Find Appendix A table
    start_idx = c.find("### Appendix A — A9 Per-Exchange Coverage")
    end_idx = c.find("### Appendix B", start_idx)
    if start_idx == -1 or end_idx == -1:
        print("❌ Appendix A not found.")
        return

    block = c[start_idx:end_idx]
    lines = block.split('\n')
    new_lines = []
    
    # Process table rows
    for line in lines:
        if line.startswith("| ") and not line.startswith("|---") and "Symbol" not in line:
            parts = line.split("|")
            if len(parts) >= 8:
                sym = parts[1].strip()
                # Status is the last column (parts[-2] because line ends with |)
                cb_status = "NOT_LISTED"
                if sym in cb_data:
                    if cb_data[sym].get("effective_min"):
                        cb_status = "TESTED"
                    elif cb_data[sym].get("quotes", {}).get("USDT", {}).get("status") == "NOT_LISTED" and cb_data[sym].get("quotes", {}).get("USD", {}).get("status") == "NOT_LISTED":
                        cb_status = "NOT_LISTED"
                
                # Reconstruct row
                parts[-2] = f" {cb_status} "
                line = "|".join(parts)
        new_lines.append(line)

    c = c[:start_idx] + '\n'.join(new_lines) + c[end_idx:]

    # 3. Update Section 13 (Known Issues)
    # Change Coinbase P0 to RESOLVED
    c = c.replace(
        "| 9 | Coinbase column pending (Appendix A) | P0 | TD | ۰۱، ۰۳ |",
        "| 9 | Coinbase column pending (Appendix A) | ✅ RESOLVED | TD | ۰۱، ۰۳ |"
    )
    c = c.replace(
        "| 12 | Bitstamp only BTC verified | P0 | TD | ۰۱ |",
        "| 12 | Bitstamp only BTC verified | P0 | TD | ۰۱ |"
    )
    
    # 4. Backup and Save
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    bk = TARGET.with_suffix(f".md.bak-{ts}")
    shutil.copy2(TARGET, bk)
    TARGET.write_text(c, encoding="utf-8")
    print("✅ TEST_MAP updated with Coinbase results.")

if __name__ == "__main__":
    main()
