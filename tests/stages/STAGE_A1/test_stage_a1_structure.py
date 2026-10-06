"""Stage A1 — Structural tests.

Only structure is verified here. No business logic, no runtime behavior.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]

APP_DIRS = [
    "app",
    "app/config",
    "app/core",
    "app/data",
    "app/market",
    "app/analysis",
    "app/bot",
    "app/api",
]

INIT_FILES = [
    "app/__init__.py",
    "app/config/__init__.py",
    "app/core/__init__.py",
    "app/data/__init__.py",
    "app/market/__init__.py",
    "app/analysis/__init__.py",
    "app/bot/__init__.py",
    "app/api/__init__.py",
]

STAGE_PY_FILES = [
    "app/core/stage_a1_version.py",
    "app/config/stage_a1_config.py",
    "conftest.py",
]

FORBIDDEN_FOLDERS = [
    "app/logging",
    "app/trading",
    "app/journal",
    "app/orderbook",
    "ledgers",
]

FORBIDDEN_IMPORTS = [
    "requests",
    "urllib",
    "http",
    "socket",
    "telegram",
    "flask",
    "httpx",
    "aiohttp",
]

FORBIDDEN_RUNTIME_TOKENS = [
    "def",
    "os.environ",
    "os.getenv",
    ".open",
    "read_text",
    "read_bytes",
]


@pytest.mark.parametrize("rel", APP_DIRS)
def test_01_structure_exists(rel: str) -> None:
    assert (ROOT / rel).is_dir(), f"missing folder: {rel}"
    assert (ROOT / "docs" / "stages" / "STAGE_A1").is_dir()


@pytest.mark.parametrize("rel", INIT_FILES)
def test_02_init_files_present(rel: str) -> None:
    assert (ROOT / rel).is_file(), f"missing init file: {rel}"


def test_03_version_identity() -> None:
    sys.path.insert(0, str(ROOT))
    try:
        from app.core.stage_a1_version import (
            CURRENT_STAGE,
            PROJECT_NAME,
            PROJECT_VERSION,
        )
    finally:
        sys.path.remove(str(ROOT))

    assert PROJECT_NAME == "Kitchen Assistant Bot"
    assert PROJECT_VERSION == "V4"
    assert CURRENT_STAGE == "A1"


def test_04_pyproject_valid() -> None:
    path = ROOT / "pyproject.toml"
    assert path.is_file()

    with path.open("rb") as handle:
        data = tomllib.load(handle)

    assert data["project"]["requires-python"] == ">=3.12"
    assert "tool" in data and "pytest" in data["tool"]
    assert "ini_options" in data["tool"]["pytest"]


def test_05_gitignore() -> None:
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")

    for token in [
        "__pycache__/",
        ".venv/",
        ".env",
        "logs/runtime/",
        "data/*",
        "!data/.gitkeep",
        "logs/*",
        "!logs/.gitkeep",
    ]:
        assert token in text, f"missing .gitignore token: {token}"


def test_06_readme() -> None:
    path = ROOT / "README.md"
    assert path.is_file()

    text = path.read_text(encoding="utf-8").strip()
    assert text
    assert "Kitchen Assistant Bot" in text
    assert "V4" in text


def test_07_conftest() -> None:
    assert (ROOT / "conftest.py").is_file()


@pytest.mark.parametrize("rel", ["scripts/.gitkeep", "data/.gitkeep", "logs/.gitkeep"])
def test_08_gitkeep(rel: str) -> None:
    assert (ROOT / rel).is_file(), f"missing gitkeep: {rel}"


@pytest.mark.parametrize("rel", FORBIDDEN_FOLDERS)
def test_09_no_forbidden_folders(rel: str) -> None:
    assert not (ROOT / rel).exists(), f"forbidden folder present: {rel}"


def test_10_stage_folder_exists() -> None:
    assert (ROOT / "docs" / "stages" / "STAGE_A1").is_dir()


def test_11_config_imports() -> None:
    sys.path.insert(0, str(ROOT))
    try:
        from app.config.stage_a1_config import PYTHON_VERSION_TARGET
    finally:
        sys.path.remove(str(ROOT))

    assert PYTHON_VERSION_TARGET == "3.12"


@pytest.mark.parametrize("rel", STAGE_PY_FILES)
def test_12_no_external_imports(rel: str) -> None:
    text = (ROOT / rel).read_text(encoding="utf-8")

    for name in FORBIDDEN_IMPORTS:
        assert f"import {name}" not in text, f"{name} imported in {rel}"
        assert f"from {name}" not in text, f"{name} imported in {rel}"


def test_13_no_runtime_logic() -> None:
    text = (ROOT / "app" / "config" / "stage_a1_config.py").read_text(encoding="utf-8")

    for token in FORBIDDEN_RUNTIME_TOKENS:
        assert token not in text, f"runtime logic token present: {token}"