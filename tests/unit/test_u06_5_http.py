import io
from urllib.error import HTTPError, URLError

import pytest

from app.market.http import (
    HTTPResult,
    classify_http_error,
    http_json,
)


class Response:
    status = 200
    headers = {"Content-Type": "application/json"}

    def __init__(self, body):
        self._body = io.BytesIO(body)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return self._body.read()

    def items(self):
        return self.headers.items()


def test_classify_http_error():
    assert classify_http_error(429, "") == "RATE_LIMIT"
    assert classify_http_error(401, "") == "AUTH_FAILED"
    assert classify_http_error(403, "") == "AUTH_FAILED"
    assert classify_http_error(404, "") == "METRIC_NOT_FOUND"
    assert classify_http_error(400, "") == "PROVIDER_ERROR"
    assert classify_http_error(503, "") == "UNAVAILABLE"
    assert classify_http_error(None, "") == "TECHNICAL_ERROR"


def test_http_json_success(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.header_items())
        captured["timeout"] = timeout
        return Response(b'{"status": {"error_code": 0}, "data": [1]}')

    monkeypatch.setattr("app.market.http.urlopen", fake_urlopen)

    result = http_json(
        "https://example.test/data",
        params={"page": 1, "empty": None},
        headers={"X-Test": "yes"},
    )

    assert isinstance(result, HTTPResult)
    assert result.ok is True
    assert result.status == 200
    assert result.payload == {"status": {"error_code": 0}, "data": [1]}
    assert result.provider_status == {"error_code": 0}
    assert result.response_headers == {"Content-Type": "application/json"}
    assert captured["url"] == "https://example.test/data?page=1"
    captured_headers = {key.lower(): value for key, value in captured["headers"].items()}
    assert captured_headers["accept"] == "application/json"
    assert captured_headers["x-test"] == "yes"
    assert captured["timeout"] == 20


def test_http_json_http_error(monkeypatch):
    body = io.BytesIO(b"provider failure")
    error = HTTPError(
        "https://example.test/data",
        429,
        "Too Many Requests",
        {},
        body,
    )

    def fake_urlopen(request, timeout):
        raise error

    monkeypatch.setattr("app.market.http.urlopen", fake_urlopen)

    result = http_json("https://example.test/data")

    assert result.ok is False
    assert result.status == 429
    assert result.error_class == "RATE_LIMIT"
    assert result.error_message.startswith("HTTP 429:")


def test_http_json_url_and_malformed_errors(monkeypatch):
    def fake_urlopen(request, timeout):
        raise URLError("offline")

    monkeypatch.setattr("app.market.http.urlopen", fake_urlopen)
    unavailable = http_json("https://example.test/data")
    assert unavailable.ok is False
    assert unavailable.error_class == "UNAVAILABLE"

    def fake_malformed(request, timeout):
        return Response(b"not json")

    monkeypatch.setattr("app.market.http.urlopen", fake_malformed)
    malformed = http_json("https://example.test/data")
    assert malformed.ok is False
    assert malformed.error_class == "MALFORMED_RESPONSE"


def test_http_json_timeout_and_generic_error(monkeypatch):
    def fake_timeout(request, timeout):
        raise TimeoutError("slow")

    monkeypatch.setattr("app.market.http.urlopen", fake_timeout)
    timeout = http_json("https://example.test/data")
    assert timeout.ok is False
    assert timeout.error_class == "TIMEOUT"

    def fake_generic(request, timeout):
        raise RuntimeError("unexpected")

    monkeypatch.setattr("app.market.http.urlopen", fake_generic)
    generic = http_json("https://example.test/data")
    assert generic.ok is False
    assert generic.error_class == "TECHNICAL_ERROR"
