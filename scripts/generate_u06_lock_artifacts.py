"""Generate the U06 SHA-256 inventory of U06 lock artifacts."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    files = [
        project_root / "U06_AUDIT_METADATA.json",
        project_root / "U06_MANIFEST.json",
        project_root / "data/historical_u05/quality/U06_DATA_QUALITY_REPORT.json",
        project_root / "data/historical_u05/quality/U06_DATA_QUALITY_SUMMARY.txt",
        project_root / "ledgers/U06_LEDGER.md",
    ]

    inventory = []
    for path in files:
        if not path.is_file():
            raise RuntimeError(f"Missing U06 artifact: {path}")
        inventory.append(
            {
                "file": str(path.relative_to(project_root)),
                "sha256": sha256_file(path),
            }
        )

    out = {
        "project": "KITCHEN_ASSISTANT",
        "version": "3.1",
        "execution_unit": "U06",
        "generated_at_utc": datetime.now(timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        ),
        "hash_algorithm": "SHA-256",
        "file_count": len(inventory),
        "files": inventory,
    }
    out_path = project_root / "U06_SHA256.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote", out_path.relative_to(project_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())