from pathlib import Path


def test_project_metadata():

    from app.core.version import (
        PROJECT_NAME,
        PROJECT_VERSION,
        EXECUTION_UNIT,
    )

    assert PROJECT_NAME == "KITCHEN_ROBOT"
    assert PROJECT_VERSION == "2.7.0-dev"
    assert EXECUTION_UNIT == "U01"


def test_configuration_boundary():

    from app.config.settings import get_settings

    settings = get_settings()

    assert settings.environment
    assert settings.timezone
    assert settings.log_level


def test_required_directories():

    root = Path(__file__).resolve().parents[1]

    required = [
        "app/config",
        "app/core",
        "app/data",
        "app/market",
        "app/scanner",
        "app/trading",
        "app/journal",
        "app/orderbook",
        "app/api",
        "tests",
        "config",
        "logs",
        "data",
        "backups",
        "ledgers",
    ]

    for directory in required:

        assert (
            root / directory
        ).is_dir(), directory
