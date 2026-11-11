import re
from pathlib import Path

TARGET = Path("tests/TEST_MAP_v3.4_FINAL.md")

def main():
    if not TARGET.exists():
        print("❌ File not found.")
        return

    c = TARGET.read_text(encoding="utf-8")
    
    # Extract Appendix A
    start = c.find("### Appendix A — A9 Per-Exchange Coverage")
    end = c.find("### Appendix B", start)
    if start == -1 or end == -1:
        print("❌ Appendix A not found.")
        return

    block = c[start:end]
    lines = block.split('\n')

    total_rows = 0
    counts = {
        'OKX': {'TESTED': 0, 'NOT_LISTED': 0, 'NOT_FOUND': 0, 'PENDING': 0},
        'Binance': {'TESTED': 0, 'NOT_LISTED': 0, 'NOT_FOUND': 0, 'PENDING': 0},
        'Bybit': {'TESTED': 0, 'NOT_LISTED': 0, 'NOT_FOUND': 0, 'PENDING': 0},
        'Bitstamp': {'TESTED': 0, 'NOT_LISTED': 0, 'NOT_FOUND': 0, 'PENDING': 0},
        'Coinbase': {'TESTED': 0, 'NOT_LISTED': 0, 'NOT_FOUND': 0, 'PENDING': 0}
    }

    for line in lines:
        if line.startswith("| ") and not line.startswith("|---") and "Symbol" not in line:
            parts = [p.strip() for p in line.split('|')]
            # parts[0] is empty, 1 is Symbol, 2-6 are exchanges
            if len(parts) >= 7:
                total_rows += 1
                exchanges = ['OKX', 'Binance', 'Bybit', 'Bitstamp', 'Coinbase']
                for i, ex in enumerate(exchanges):
                    status = parts[i+2]
                    if status in counts[ex]:
                        counts[ex][status] += 1
                    elif status not in ['-', '?']:
                        print(f"⚠️ Unknown status '{status}' for {ex} in row: {parts[1]}")

    print("=== Validation Results (Appendix A) ===")
    print(f"Total asset rows: {total_rows} (Expected: 150)\n")
    
    print(f"{'Exchange':<10} | {'TESTED':<8} | {'NOT_LISTED':<10} | {'NOT_FOUND':<10} | {'PENDING':<8}")
    print("-" * 55)
    for ex in counts:
        c_t = counts[ex]['TESTED']
        c_nl = counts[ex]['NOT_LISTED']
        c_nf = counts[ex]['NOT_FOUND']
        c_p = counts[ex]['PENDING']
        print(f"{ex:<10} | {c_t:<8} | {c_nl:<10} | {c_nf:<10} | {c_p:<8}")

    print("\n=== Section 13 Status ===")
    sec13 = c.find("## Section 13 — Known Issues")
    if sec13 != -1:
        block13 = c[sec13:]
        res_lines = [l for l in block13.split('\n') if 'RESOLVED' in l]
        print(f"RESOLVED issues: {len(res_lines)}")
        for l in res_lines:
            print(" ", l[:80] + "...")

if __name__ == "__main__":
    main()
