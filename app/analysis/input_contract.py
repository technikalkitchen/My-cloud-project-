"""Stage 7 (U07) Unit 7.1 — Input contract.

Stage 7 consumes the frozen U06.5 Market Data Foundation as its ONLY
source of truth. This module validates that the U07 adapter produced by
U06.5 contains every field Stage 7 requires, and it exposes a single
validated contract object for Units 7.2-7.4.

No market-data acquisition happens here. No scenario logic. No
intelligence/narrative logic.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.analysis.metrics import _is_finite_number


# ---------------------------------------------------------------------------
# Required fields
# ---------------------------------------------------------------------------

_REQUIRED_ADAPTER_FIELDS: List[str] = [
    "SOURCE_CELL",
    "SCHEMA_VERSION",
    "RUN_ID",
    "SNAPSHOT_ID",
    "SNAPSHOT_HASH",
    "DATA_STATUS",
    "TIMEFRAME",
    "DATASET_MODE",
    "ANALYSIS_RANGE",
    "AVAILABLE_RANGE",
    "HISTORY_STATUS",
    "HISTORY_SOURCE",
    "HISTORY_COVERAGE",
    "HISTORY_POINTS",
    "TOTAL_SERIES",
    "TOTAL2_SERIES",
    "TOTAL3_SERIES",
    "BTC_D_SERIES",
    "USDT_D_SERIES",
    "CURRENT_VALUES",
    "PROVIDER_METADATA",
    "DEFINITIONS",
    "PROVENANCE",
    "FRESHNESS",
    "COVERAGE",
    "NO_DATA_FABRICATION",
]


def _is_non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0


def _series_is_finite_positive(values: Any) -> bool:
    if not _is_non_empty_list(values):
        return False
    return all(_is_finite_number(v) and float(v) > 0.0 for v in values)


# ---------------------------------------------------------------------------
# Contract dataclass
# ---------------------------------------------------------------------------

@dataclass
class Stage7InputContract:
    source_cell: str
    schema_version: str
    run_id: str
    snapshot_id: str
    snapshot_hash: str
    data_status: str
    timeframe: str
    dataset_mode: str

    analysis_range: Dict[str, Any]
    available_range: Dict[str, Any]
    history_status: str
    history_source: str
    history_coverage: Optional[float]
    history_points: List[Dict[str, Any]]

    total_series: List[float]
    total2_series: List[float]
    total3_series: List[float]
    btc_d_series: List[float]
    usdt_d_series: List[float]

    current_values: Dict[str, Any]
    provider_metadata: Dict[str, Any]
    definitions: Dict[str, Any]
    provenance: Dict[str, Any]
    freshness: Dict[str, Any]
    coverage: Dict[str, Any]

    no_data_fabrication: bool

    validation: Dict[str, Any]
    errors: List[str]
    warnings: List[str]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _require(adapter: Dict[str, Any], field: str) -> Any:
    if field not in adapter or adapter[field] is None:
        raise ValueError(
            f"MISSING_REQUIRED_FIELD: {field}"
        )
    return adapter[field]


def validate_stage7_input(
    adapter: Dict[str, Any],
    *,
    max_freshness_age_seconds: Optional[float] = None,
) -> Stage7InputContract:
    """Validate the U07 adapter produced by U06.5 and build the Stage 7 contract.

    Rules enforced here:
      * Every required adapter field must be present and non-null.
      * SOURCE_CELL must be U06.5 (frozen foundation identity).
      * DATA_STATUS must be a non-empty status string.
      * TOTAL_SERIES and USDT_D_SERIES must be non-empty, finite, positive.
      * History must be present (>= 2 points) for movement analysis.
      * NO_DATA_FABRICATION must be True.
      * Freshness must be FRESH or UNAVAILABLE (STALE is rejected).
      * No market-data acquisition is performed.
    """
    if not isinstance(adapter, dict):
        raise TypeError("adapter must be a dict.")

    for field in _REQUIRED_ADAPTER_FIELDS:
        _require(adapter, field)

    source_cell = str(adapter["SOURCE_CELL"])
    if source_cell != "U06.5":
        raise ValueError(
            f"SOURCE_CELL must be U06.5, got {source_cell!r}."
        )

    data_status = str(adapter["DATA_STATUS"])
    if not data_status:
        raise ValueError("DATA_STATUS must be non-empty.")

    total_series = adapter["TOTAL_SERIES"]
    usdt_d_series = adapter["USDT_D_SERIES"]
    total2_series = adapter["TOTAL2_SERIES"]
    total3_series = adapter["TOTAL3_SERIES"]
    btc_d_series = adapter["BTC_D_SERIES"]

    if not _series_is_finite_positive(total_series):
        raise ValueError(
            "TOTAL_SERIES must be a non-empty list of finite positive values."
        )
    if not _series_is_finite_positive(usdt_d_series):
        raise ValueError(
            "USDT_D_SERIES must be a non-empty list of finite positive values."
        )
    if not _series_is_finite_positive(total2_series):
        raise ValueError(
            "TOTAL2_SERIES must be a non-empty list of finite positive values."
        )
    if not _series_is_finite_positive(total3_series):
        raise ValueError(
            "TOTAL3_SERIES must be a non-empty list of finite positive values."
        )
    if not _series_is_finite_positive(btc_d_series):
        raise ValueError(
            "BTC_D_SERIES must be a non-empty list of finite positive values."
        )

    if not (
        len(total_series)
        == len(usdt_d_series)
        == len(total2_series)
        == len(total3_series)
        == len(btc_d_series)
    ):
        raise ValueError(
            "All series must have equal length."
        )

    if len(total_series) < 2:
        raise ValueError(
            "HISTORY_POINTS must contain at least 2 observations."
        )

    if adapter["NO_DATA_FABRICATION"] is not True:
        raise ValueError(
            "NO_DATA_FABRICATION must be True."
        )

    history_status = str(adapter["HISTORY_STATUS"])
    if history_status not in {"VALIDATED", "PARTIAL"}:
        raise ValueError(
            f"HISTORY_STATUS must be VALIDATED or PARTIAL, got {history_status!r}."
        )

    freshness = adapter["FRESHNESS"]
    freshness_status = (
        freshness.get("status") if isinstance(freshness, dict) else None
    )
    if freshness_status not in {"FRESH", "UNAVAILABLE"}:
        raise ValueError(
            f"FRESHNESS.status must be FRESH or UNAVAILABLE, got {freshness_status!r}."
        )

    if max_freshness_age_seconds is not None:
        if not isinstance(max_freshness_age_seconds, (int, float)):
            raise TypeError("max_freshness_age_seconds must be numeric.")
        if max_freshness_age_seconds < 0:
            raise ValueError("max_freshness_age_seconds must be >= 0.")

    analysis_range = adapter["ANALYSIS_RANGE"]
    if not isinstance(analysis_range, dict):
        raise ValueError("ANALYSIS_RANGE must be a dict.")

    available_range = adapter["AVAILABLE_RANGE"]
    if not isinstance(available_range, dict):
        raise ValueError("AVAILABLE_RANGE must be a dict.")

    history_points = adapter["HISTORY_POINTS"]
    if not isinstance(history_points, list):
        raise ValueError("HISTORY_POINTS must be a list.")

    coverage = adapter["COVERAGE"]
    if not isinstance(coverage, dict):
        raise ValueError("COVERAGE must be a dict.")

    provenance = adapter["PROVENANCE"]
    if not isinstance(provenance, dict):
        raise ValueError("PROVENANCE must be a dict.")

    provider_metadata = adapter["PROVIDER_METADATA"]
    if not isinstance(provider_metadata, dict):
        raise ValueError("PROVIDER_METADATA must be a dict.")

    definitions = adapter["DEFINITIONS"]
    if not isinstance(definitions, dict):
        raise ValueError("DEFINITIONS must be a dict.")

    current_values = adapter["CURRENT_VALUES"]
    if not isinstance(current_values, dict):
        raise ValueError("CURRENT_VALUES must be a dict.")

    return Stage7InputContract(
        source_cell=source_cell,
        schema_version=str(adapter["SCHEMA_VERSION"]),
        run_id=str(adapter["RUN_ID"]),
        snapshot_id=str(adapter["SNAPSHOT_ID"]),
        snapshot_hash=str(adapter["SNAPSHOT_HASH"]),
        data_status=data_status,
        timeframe=str(adapter["TIMEFRAME"]),
        dataset_mode=str(adapter["DATASET_MODE"]),
        analysis_range=analysis_range,
        available_range=available_range,
        history_status=history_status,
        history_source=str(adapter["HISTORY_SOURCE"]),
        history_coverage=adapter["HISTORY_COVERAGE"],
        history_points=history_points,
        total_series=[float(v) for v in total_series],
        total2_series=[float(v) for v in total2_series],
        total3_series=[float(v) for v in total3_series],
        btc_d_series=[float(v) for v in btc_d_series],
        usdt_d_series=[float(v) for v in usdt_d_series],
        current_values=current_values,
        provider_metadata=provider_metadata,
        definitions=definitions,
        provenance=provenance,
        freshness=freshness,
        coverage=coverage,
        no_data_fabrication=True,
        validation={
            "validated_at_input_contract": True,
            "required_fields_checked": list(_REQUIRED_ADAPTER_FIELDS),
            "series_lengths": {
                "total": len(total_series),
                "usdt_d": len(usdt_d_series),
            },
            "freshness_status": freshness_status,
            "max_freshness_age_seconds": (
                max_freshness_age_seconds
            ),
        },
        errors=[str(e) for e in adapter.get("errors", []) or []],
        warnings=[str(w) for w in adapter.get("warnings", []) or []],
    )


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def input_contract_self_tests() -> Dict[str, Any]:
    """Deterministic self-test for the Stage 7 input contract."""
    from app.config.quality import FRESHNESS_THRESHOLD_SECONDS

    now = "2026-09-11T16:30:00+00:00"
    points = [
        {
            "timestamp": now,
            "KITCHEN_TOTAL_TOP125": 3_000_000_000.0,
            "KITCHEN_USDT_D": 5.0,
            "KITCHEN_BTC_D": 40.0,
        },
        {
            "timestamp": now,
            "KITCHEN_TOTAL_TOP125": 3_100_000_000.0,
            "KITCHEN_USDT_D": 4.8,
            "KITCHEN_BTC_D": 41.0,
        },
    ]

    valid_adapter = {
        "SOURCE_CELL": "U06.5",
        "SCHEMA_VERSION": "U06_5_SCHEMA_V6_0",
        "RUN_ID": "RUN",
        "SNAPSHOT_ID": "SNAP",
        "SNAPSHOT_HASH": "abc",
        "DATA_STATUS": "FROZEN",
        "TIMEFRAME": "5m",
        "DATASET_MODE": "SNAPSHOT",
        "ANALYSIS_RANGE": {"start": "2026-09-10", "end": "2026-09-11"},
        "AVAILABLE_RANGE": {"start": now, "end": now},
        "HISTORY_STATUS": "VALIDATED",
        "HISTORY_SOURCE": "KITCHEN_RECORDED",
        "HISTORY_COVERAGE": 1.0,
        "HISTORY_POINTS": points,
        "TOTAL_SERIES": [p["KITCHEN_TOTAL_TOP125"] for p in points],
        "TOTAL2_SERIES": [p["KITCHEN_TOTAL_TOP125"] for p in points],
        "TOTAL3_SERIES": [p["KITCHEN_TOTAL_TOP125"] for p in points],
        "BTC_D_SERIES": [p["KITCHEN_BTC_D"] for p in points],
        "USDT_D_SERIES": [p["KITCHEN_USDT_D"] for p in points],
        "CURRENT_VALUES": {
            "KITCHEN_TOTAL_TOP125": 3_100_000_000.0,
            "KITCHEN_USDT_D": 4.8,
        },
        "PROVIDER_METADATA": {"provider": "coinmarketcap"},
        "DEFINITIONS": {
            "KITCHEN_TOTAL_TOP125": "SUM(MARKET_CAP of ranks 1-125)",
            "KITCHEN_USDT_D": "USDT_MARKET_CAP / KITCHEN_TOTAL_TOP125 * 100",
        },
        "PROVENANCE": {"SOURCE": "coinmarketcap"},
        "FRESHNESS": {
            "status": "FRESH",
            "threshold_seconds": FRESHNESS_THRESHOLD_SECONDS,
        },
        "COVERAGE": {"top125": 1.0},
        "NO_DATA_FABRICATION": True,
        "errors": [],
        "warnings": [],
    }

    tests: Dict[str, Any] = {}

    contract = validate_stage7_input(valid_adapter)
    tests["valid_adapter_passes"] = (
        contract.source_cell == "U06.5"
        and contract.total_series == [3_000_000_000.0, 3_100_000_000.0]
        and contract.usdt_d_series == [5.0, 4.8]
        and contract.no_data_fabrication is True
    )

    bad_source = dict(valid_adapter)
    bad_source["SOURCE_CELL"] = "U08"
    try:
        validate_stage7_input(bad_source)
        tests["wrong_source_rejected"] = False
    except ValueError:
        tests["wrong_source_rejected"] = True

    missing = dict(valid_adapter)
    missing.pop("SNAPSHOT_HASH")
    try:
        validate_stage7_input(missing)
        tests["missing_field_rejected"] = False
    except ValueError:
        tests["missing_field_rejected"] = True

    stale = dict(valid_adapter)
    stale["FRESHNESS"] = {
        "status": "STALE",
        "threshold_seconds": FRESHNESS_THRESHOLD_SECONDS,
    }
    try:
        validate_stage7_input(stale)
        tests["stale_freshness_rejected"] = False
    except ValueError:
        tests["stale_freshness_rejected"] = True

    short = dict(valid_adapter)
    short["TOTAL_SERIES"] = [3_000_000_000.0]
    try:
        validate_stage7_input(short)
        tests["short_series_rejected"] = False
    except ValueError:
        tests["short_series_rejected"] = True

    bad_values = dict(valid_adapter)
    bad_values["USDT_D_SERIES"] = [5.0, float("nan")]
    try:
        validate_stage7_input(bad_values)
        tests["non_finite_rejected"] = False
    except ValueError:
        tests["non_finite_rejected"] = True

    zero = dict(valid_adapter)
    zero["TOTAL_SERIES"] = [0.0, 100.0]
    try:
        validate_stage7_input(zero)
        tests["non_positive_rejected"] = False
    except ValueError:
        tests["non_positive_rejected"] = True

    mismatch = dict(valid_adapter)
    mismatch["TOTAL_SERIES"] = [1.0, 2.0, 3.0]
    try:
        validate_stage7_input(mismatch)
        tests["length_mismatch_rejected"] = False
    except ValueError:
        tests["length_mismatch_rejected"] = True

    fabricated = dict(valid_adapter)
    fabricated["NO_DATA_FABRICATION"] = False
    try:
        validate_stage7_input(fabricated)
        tests["fabrication_flag_rejected"] = False
    except ValueError:
        tests["fabrication_flag_rejected"] = True

    not_dict = dict(valid_adapter)
    not_dict["PROVENANCE"] = None
    try:
        validate_stage7_input(not_dict)
        tests["non_dict_section_rejected"] = False
    except ValueError:
        tests["non_dict_section_rejected"] = True

    try:
        validate_stage7_input("not a dict")
        tests["non_dict_adapter_rejected"] = False
    except TypeError:
        tests["non_dict_adapter_rejected"] = True

    return {
        "status": "PASS" if all(tests.values()) else "FAIL",
        "passed": sum(tests.values()),
        "total": len(tests),
        "tests": tests,
    }