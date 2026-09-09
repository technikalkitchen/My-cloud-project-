from pathlib import Path


def test_flask_app_creation():

    from app.api.app import create_app

    app = create_app()

    assert app is not None


def test_root_endpoint():

    from app.api.app import create_app

    app = create_app()

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "running"


def test_health_endpoint():

    from app.api.app import create_app

    app = create_app()

    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "ok"
    assert data["project"] == "KITCHEN_ROBOT"
    assert data["execution_unit"] == "U01"


def test_sub_daily_standard_timeframe_warning():

    from app.api.app import validate_timeframe_guard

    for timeframe in [
        "M1",
        "M5",
        "M15",
        "H1",
        "H4",
    ]:

        result = validate_timeframe_guard(
            timeframe
        )

        assert result["valid"] is True

        assert result["warning"] is not None

        assert result["is_sub_daily"] is True

        assert (
            result["reason"]
            == "SUB_DAILY_TIMEFRAME"
        )


def test_daily_timeframe_has_no_sub_daily_warning():

    from app.api.app import validate_timeframe_guard

    result = validate_timeframe_guard(
        "D1"
    )

    assert result["valid"] is True
    assert result["warning"] is None
    assert result["is_sub_daily"] is False


def test_weekly_timeframe_has_no_sub_daily_warning():

    from app.api.app import validate_timeframe_guard

    result = validate_timeframe_guard(
        "D7"
    )

    assert result["valid"] is True
    assert result["warning"] is None
    assert result["is_sub_daily"] is False


def test_custom_range_below_daily_warning():

    from app.api.app import validate_timeframe_guard

    result = validate_timeframe_guard(
        "CUSTOM",
        "28-08-2026 10:00",
        "28-08-2026 18:00",
    )

    assert result["valid"] is True

    assert result["warning"] is not None

    assert result["is_sub_daily"] is True

    assert (
        result["reason"]
        == "SUB_DAILY_CUSTOM_RANGE"
    )


def test_custom_range_exactly_daily():

    from app.api.app import validate_timeframe_guard

    result = validate_timeframe_guard(
        "CUSTOM",
        "28-08-2026 10:00",
        "29-08-2026 10:00",
    )

    assert result["valid"] is True
    assert result["warning"] is None
    assert result["is_sub_daily"] is False


def test_custom_range_above_daily():

    from app.api.app import validate_timeframe_guard

    result = validate_timeframe_guard(
        "CUSTOM",
        "28-08-2026 10:00",
        "30-08-2026 10:00",
    )

    assert result["valid"] is True
    assert result["warning"] is None
    assert result["is_sub_daily"] is False


def test_invalid_custom_range_format():

    from app.api.app import validate_timeframe_guard

    result = validate_timeframe_guard(
        "CUSTOM",
        "2026-08-28 10:00",
        "2026-08-28 18:00",
    )

    assert result["valid"] is False

    assert (
        result["reason"]
        == "INVALID_CUSTOM_RANGE_FORMAT"
    )


def test_invalid_custom_range_order():

    from app.api.app import validate_timeframe_guard

    result = validate_timeframe_guard(
        "CUSTOM",
        "29-08-2026 10:00",
        "28-08-2026 10:00",
    )

    assert result["valid"] is False

    assert (
        result["reason"]
        == "INVALID_CUSTOM_RANGE_ORDER"
    )


def test_unsupported_timeframe():

    from app.api.app import validate_timeframe_guard

    result = validate_timeframe_guard(
        "UNKNOWN"
    )

    assert result["valid"] is False

    assert (
        result["reason"]
        == "UNSUPPORTED_TIMEFRAME"
    )


def test_wsgi_entrypoint():

    import wsgi

    assert wsgi.application is not None


def test_runtime_files():

    root = Path(__file__).resolve().parents[1]

    assert (
        root / "wsgi.py"
    ).is_file()

    assert (
        root / "scripts/start_wsgi.sh"
    ).is_file()

    assert (
        root / "app/config/runtime.py"
    ).is_file()
