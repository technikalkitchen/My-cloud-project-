"""U06.5-A core utilities.

Portable, stdlib-only helpers shared by the A layer (and later by B).
No Colab imports, no notebook-host paths, no secrets in output.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_float(value: Any) -> Optional[float]:
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except Exception:
        return None


def safe_int(value: Any) -> Optional[int]:
    try:
        if isinstance(value, bool):
            return None
        return int(value)
    except Exception:
        return None


def parse_timestamp(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        s = str(value).strip()
        if not s:
            return None
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(s)
        except Exception:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def timestamp_age_seconds(source_timestamp: Any, retrieved_at: Any) -> Optional[float]:
    src = parse_timestamp(source_timestamp)
    ret = parse_timestamp(retrieved_at)
    if not src or not ret:
        return None
    return max(0.0, (ret - src).total_seconds())


def safe_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): safe_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe_json(v) for v in value]
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        safe_json(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_obj(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


_SECRET_WORDS = (
    "api_key", "apikey", "authorization", "token", "secret",
    "password", "credential", "private_key",
)


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        result: Dict[str, Any] = {}
        for key, item in value.items():
            if any(word in str(key).lower() for word in _SECRET_WORDS):
                result[str(key)] = "[REDACTED]"
            else:
                result[str(key)] = redact(item)
        return result
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def safe_name(value: Any) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value))


def deep_copy(value: Any) -> Any:
    return copy.deepcopy(value)


def resolve_root() -> Path:
    """Portable project-root discovery.

    Notebook-host-specific content trees (Colab /content, drive mounts) are
    explicitly excluded. Credentials are never read from notebook state.
    """
    candidates: List[Path] = []

    def _portable_candidate(path: Path) -> bool:
        try:
            resolved = path.expanduser().resolve()
            parts = {part.lower() for part in resolved.parts}
            if "content" in parts:
                return False
            return resolved.is_dir()
        except Exception:
            return False

    explicit = os.getenv("KITCHEN_ROOT", "").strip()
    if explicit:
        explicit_path = Path(explicit).expanduser()
        if _portable_candidate(explicit_path):
            return explicit_path.resolve()
        candidates.append(explicit_path)

    try:
        cwd = Path.cwd()
        if _portable_candidate(cwd):
            candidates.append(cwd)
    except Exception:
        pass

    candidates.extend([Path("/mnt/data"), Path("/tmp")])

    existing: List[Path] = []
    for candidate in candidates:
        try:
            candidate = candidate.resolve()
            if candidate.is_dir() and candidate not in existing:
                existing.append(candidate)
        except Exception:
            continue

    markers = (
        "Kitchen Assistant",
        "data",
        "app",
        "requirements.txt",
    )

    for candidate in existing:
        try:
            names = {p.name for p in candidate.iterdir()}
            if any(
                marker in name
                for name in names
                for marker in markers
            ):
                return candidate
        except Exception:
            continue

    return existing[0] if existing else Path("/tmp")


def get_root() -> Path:
    """Lazy project root resolution. No side effects."""
    return resolve_root()


def get_data_dir() -> Path:
    """Lazy data directory path. No directory creation."""
    return get_root() / "data"


def get_raw_dir() -> Path:
    """Lazy raw data directory path. No directory creation."""
    return get_data_dir() / "raw" / "U06_5"


def get_snapshot_dir() -> Path:
    """Lazy snapshot directory path. No directory creation."""
    return get_data_dir() / "snapshots" / "U06_5"


def get_audit_dir() -> Path:
    """Lazy audit directory path. No directory creation."""
    return get_data_dir() / "audit" / "U06_5"


def get_history_dir() -> Path:
    """Lazy history directory path. No directory creation."""
    return get_data_dir() / "history" / "U06_5"


def ensure_dirs() -> None:
    """Explicitly create U06.5 directories when needed.

    Called by Layer B or runtime code, never at import time.
    Respects AUTO_PERSIST_SNAPSHOT = False from quality config.
    """
    from app.config.quality import AUTO_PERSIST_SNAPSHOT

    if not AUTO_PERSIST_SNAPSHOT:
        return

    for directory in (
        get_data_dir(),
        get_raw_dir(),
        get_snapshot_dir(),
        get_audit_dir(),
        get_history_dir(),
    ):
        directory.mkdir(parents=True, exist_ok=True)