"""Stage 8 (U08) Unit 8.8 — Narratives focused tests.

Covers the 27 locked Persian narratives from ``app.analysis.u08_narratives``.
"""
from __future__ import annotations

import pytest

from app.analysis.u08_narratives import (
    NARRATIVES,
    get_narrative,
    validate_narratives,
    NARRATIVE_VALIDATION,
)


# ---- Structure validation ----------------------------------------------------

def test_narratives_dict_has_9_scenarios():
    assert set(NARRATIVES.keys()) == set(range(1, 10))


def test_each_scenario_has_3_patterns():
    for scenario_id in range(1, 10):
        assert len(NARRATIVES[scenario_id]) == 3


def test_total_patterns_is_27():
    total = sum(len(NARRATIVES[s]) for s in range(1, 10))
    assert total == 27


def test_each_pattern_has_required_fields():
    for scenario_id in range(1, 10):
        for pattern in NARRATIVES[scenario_id]:
            assert "pattern" in pattern
            assert "title" in pattern
            assert "text" in pattern
            assert isinstance(pattern["text"], str)
            assert len(pattern["text"].strip()) > 0


# ---- Exact text preservation (LOCKED — DO NOT REWRITE) ----------------------

def test_scenario_1_pattern_1_text_exact():
    n = get_narrative(1, 1)
    assert n["pattern"] == "Pattern 1"
    assert n["title"] == "🟢 BTC Strength"
    assert n["text"].startswith("رشد هم‌زمان BTC و BTC.D")
    assert "بیت‌کوین در حرکت فعلی قدرت بیشتری" in n["text"]
    assert "BTC همچنان یکی از دارایی‌های اصلی" in n["text"]


def test_scenario_1_pattern_2_text_exact():
    n = get_narrative(1, 2)
    assert n["pattern"] == "Pattern 2"
    assert n["title"] == "🟢 BTC Strength / Relative Movers"
    assert n["text"].startswith("افزایش BTC همراه با افزایش BTC.D")
    assert "BTC همچنان معیار اصلی مقایسه" in n["text"]


def test_scenario_1_pattern_3_text_exact():
    n = get_narrative(1, 3)
    assert n["pattern"] == "Pattern 3"
    assert n["title"] == "🟢 BTC Dominance Strength"
    assert n["text"].startswith("وقتی BTC و BTC.D هر دو صعودی هستند")
    assert "BTC همچنان در کنار این دارایی‌ها" in n["text"]


def test_scenario_2_pattern_1_text_exact():
    n = get_narrative(2, 1)
    assert n["pattern"] == "Pattern 1"
    assert n["title"] == "🟢 Altcoin Strength"
    assert n["text"].startswith("رشد BTC در کنار کاهش BTC.D")
    assert "BTC همچنان معیار اصلی مقایسه" in n["text"]


def test_scenario_2_pattern_2_text_exact():
    n = get_narrative(2, 2)
    assert n["pattern"] == "Pattern 2"
    assert n["title"] == "🟢 Altcoin Relative Strength"
    assert n["text"].startswith("وقتی BTC در حال رشد است اما BTC.D کاهش می‌یابد")
    assert "BTC همچنان معیار اصلی سنجش" in n["text"]


def test_scenario_2_pattern_3_text_exact():
    n = get_narrative(2, 3)
    assert n["pattern"] == "Pattern 3"
    assert n["title"] == "🟢 Broad Altcoin Participation"
    assert n["text"].startswith("افزایش BTC همراه با افت BTC.D")
    assert "BTC معیار اصلی مقایسه این حرکات" in n["text"]


def test_scenario_3_all_patterns_same_title():
    # Scenario 3 has 3 patterns all titled "🟢 Broad Market Strength"
    for pi in (1, 2, 3):
        n = get_narrative(3, pi)
        assert n["title"] == "🟢 Broad Market Strength"
        assert n["text"].startswith(("بیت‌کوین در حال رشد", "رشد BTC همراه", "وقتی BTC صعودی"))
        assert "BTC" in n["text"]


def test_scenario_4_pattern_1_text_exact():
    n = get_narrative(4, 1)
    assert n["pattern"] == "Pattern 1"
    assert n["title"] == "🔴 Altcoin Weakness"
    assert n["text"].startswith("کاهش BTC در کنار افزایش BTC.D")
    assert "BTC همچنان معیار اصلی مقایسه" in n["text"]


def test_scenario_4_pattern_2_text_exact():
    n = get_narrative(4, 2)
    assert n["pattern"] == "Pattern 2"
    assert n["title"] == "🔴 Altcoin Relative Weakness"
    assert n["text"].startswith("وقتی BTC در حال کاهش است اما BTC.D افزایش می‌یابد")
    assert "BTC همچنان معیار اصلی سنجش" in n["text"]


def test_scenario_4_pattern_3_text_exact():
    n = get_narrative(4, 3)
    assert n["pattern"] == "Pattern 3"
    assert n["title"] == "🔴 Broad Altcoin Weakness"
    assert n["text"].startswith("کاهش BTC همراه با افزایش BTC.D")
    assert "BTC معیار اصلی مقایسه" in n["text"]


def test_scenario_5_pattern_1_text_exact():
    n = get_narrative(5, 1)
    assert n["pattern"] == "Pattern 1"
    assert n["title"] == "🟡 BTC Weakness / Alt Relative Strength"
    assert n["text"].startswith("کاهش هم‌زمان BTC و BTC.D")


def test_scenario_5_pattern_2_text_exact():
    n = get_narrative(5, 2)
    assert n["pattern"] == "Pattern 2"
    assert n["title"] == "🟡 Altcoin Relative Performance"
    assert n["text"].startswith("وقتی BTC نزولی است و BTC.D نیز کاهش می‌یابد")


def test_scenario_5_pattern_3_text_exact():
    n = get_narrative(5, 3)
    assert n["pattern"] == "Pattern 3"
    assert n["title"] == "🟡 Relative Performance Under BTC Weakness"
    assert n["text"].startswith("افت BTC همراه با کاهش BTC.D")


def test_scenario_6_pattern_1_text_exact():
    n = get_narrative(6, 1)
    assert n["pattern"] == "Pattern 1"
    assert n["title"] == "🔴 Broad Market Weakness"
    assert n["text"].startswith("کاهش BTC در حالی که BTC.D در محدوده رنج")


def test_scenario_6_pattern_2_text_exact():
    n = get_narrative(6, 2)
    assert n["pattern"] == "Pattern 2"
    assert n["title"] == "🔴 Relative Weakness Under BTC Decline"
    assert n["text"].startswith("وقتی BTC نزولی است اما BTC.D رنج می‌زند")


def test_scenario_6_pattern_3_text_exact():
    n = get_narrative(6, 3)
    assert n["pattern"] == "Pattern 3"
    assert n["title"] == "🔴 Coin/BTC Relative Weakness"
    assert n["text"].startswith("افت BTC همراه با رنج بودن BTC.D")


def test_scenario_7_pattern_1_text_exact():
    n = get_narrative(7, 1)
    assert n["pattern"] == "Pattern 1"
    assert n["title"] == "Altcoin Weakness During BTC Range"
    assert n["text"].startswith("رنج بودن BTC همراه با افزایش BTC.D")


def test_scenario_7_pattern_2_text_exact():
    n = get_narrative(7, 2)
    assert n["pattern"] == "Pattern 2"
    assert n["title"] == "BTC Dominance Gain"
    assert n["text"].startswith("ثبات نسبی BTC در کنار افزایش BTC.D")


def test_scenario_7_pattern_3_text_exact():
    n = get_narrative(7, 3)
    assert n["pattern"] == "Pattern 3"
    assert n["title"] == "Relative Altcoin Weakness"
    assert n["text"].startswith("وقتی BTC در محدوده رنج قرار دارد")


def test_scenario_8_pattern_1_text_exact():
    n = get_narrative(8, 1)
    assert n["pattern"] == "Pattern 1"
    assert n["title"] == "Altcoin Strength During BTC Range"
    assert n["text"].startswith("رنج بودن BTC همراه با کاهش BTC.D")


def test_scenario_8_pattern_2_text_exact():
    n = get_narrative(8, 2)
    assert n["pattern"] == "Pattern 2"
    assert n["title"] == "BTC Dominance Decline"
    assert n["text"].startswith("ثبات نسبی BTC در کنار کاهش BTC.D")


def test_scenario_8_pattern_3_text_exact():
    n = get_narrative(8, 3)
    assert n["pattern"] == "Pattern 3"
    assert n["title"] == "Relative Altcoin Strength"
    assert n["text"].startswith("وقتی BTC در محدوده رنج قرار دارد")


def test_scenario_9_pattern_1_text_exact():
    n = get_narrative(9, 1)
    assert n["pattern"] == "Pattern 1"
    assert n["title"] == "Balanced Market"
    assert n["text"].startswith("رنج بودن هم‌زمان BTC و BTC.D")


def test_scenario_9_pattern_2_text_exact():
    n = get_narrative(9, 2)
    assert n["pattern"] == "Pattern 2"
    assert n["title"] == "BTC Relative Movement"
    assert n["text"].startswith("وقتی BTC و BTC.D هر دو در محدوده رنج")


def test_scenario_9_pattern_3_text_exact():
    n = get_narrative(9, 3)
    assert n["pattern"] == "Pattern 3"
    assert n["title"] == "Relative Strength in a Flat Market"
    assert n["text"].startswith("رنج بودن BTC در کنار رنج بودن BTC.D")


# ---- get_narrative function --------------------------------------------------

def test_get_narrative_returns_copy():
    n1 = get_narrative(1, 1)
    n2 = get_narrative(1, 1)
    assert n1 is not n2
    assert n1 == n2


def test_get_narrative_invalid_scenario_raises():
    with pytest.raises(ValueError):
        get_narrative(0, 1)
    with pytest.raises(ValueError):
        get_narrative(10, 1)


def test_get_narrative_invalid_pattern_raises():
    with pytest.raises(ValueError):
        get_narrative(1, 0)
    with pytest.raises(ValueError):
        get_narrative(1, 4)


# ---- validate_narratives -----------------------------------------------------

def test_validate_narratives_returns_locked():
    result = validate_narratives()
    assert result["scenarios"] == 9
    assert result["patterns"] == 27
    assert result["status"] == "LOCKED"


def test_NARRATIVE_VALIDATION_constant():
    assert NARRATIVE_VALIDATION["scenarios"] == 9
    assert NARRATIVE_VALIDATION["patterns"] == 27
    assert NARRATIVE_VALIDATION["status"] == "LOCKED"