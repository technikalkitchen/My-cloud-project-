"""U06.5-A HTTP / provider-response model.

Portable JSON HTTP client using only the standard library. Error classes are
explicit so retry policy can be decided deterministically without guessing.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.core.u06_5 import utc_now
from app.config.quality import HTTP_TIMEOUT_SECONDS, VERSION


@dataclass
class HTTPResult:
    ok: bool
    status: Optional[int]
    payload: Any
    retrieved_at: str
    elapsed_seconds: float
    provider_status: Any = None
    error_class: Optional[str] = None
    error_message: Optional[str] = None
    response_headers: Optional[Dict[str, str]] = None


def classify_http_error(status: Optional[int], body: str) -> str:
    if status == 429:
        return "RATE_LIMIT"
    if status in (401, 403):
        return "AUTH_FAILED"
    if status == 404:
        return "METRIC_NOT_FOUND"
    if status is not None and 400 <= status < 500:
        return "PROVIDER_ERROR"
    if status is not None and status >= 500:
        return "UNAVAILABLE"
    return "TECHNICAL_ERROR"


# Error classes that may justify a bounded retry.
RETRYABLE_ERROR_CLASSES = {
    "TIMEOUT",
    "RATE_LIMIT",
    "UNAVAILABLE",
    "TECHNICAL_ERROR",
    "PROVIDER_ERROR",
}


def http_json(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> HTTPResult:
    query = ""
    if params:
        query = "?" + urlencode(
            {k: v for k, v in params.items() if v is not None}
        )

    started = time.time()
    retrieved_at = utc_now()

    request_headers = {
        "Accept": "application/json",
        "User-Agent": f"Kitchen-Assistant-U06.5/{VERSION}",
    }
    if headers:
        request_headers.update(headers)

    # Never allow a credential to leak through serialized request data.
    request_headers = {
        str(k): str(v)
        for k, v in request_headers.items()
    }

    try:
        req = Request(url + query, headers=request_headers)
        with urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as response:
            body = response.read()
            payload = json.loads(body.decode("utf-8"))
            response_headers = {
                str(k): str(v) for k, v in response.headers.items()
            }
            provider_status = None
            if isinstance(payload, dict):
                provider_status = payload.get("status")
            return HTTPResult(
                ok=True,
                status=response.status,
                payload=payload,
                retrieved_at=retrieved_at,
                elapsed_seconds=time.time() - started,
                provider_status=provider_status,
                response_headers=response_headers,
            )
    except HTTPError as exc:
        try:
            body = exc.read().decode("utf-8", "replace")[:2000]
        except Exception:
            body = ""
        return HTTPResult(
            ok=False,
            status=exc.code,
            payload=None,
            retrieved_at=retrieved_at,
            elapsed_seconds=time.time() - started,
            error_class=classify_http_error(exc.code, body),
            error_message=f"HTTP {exc.code}: {body}",
        )
    except URLError as exc:
        return HTTPResult(
            ok=False,
            status=None,
            payload=None,
            retrieved_at=retrieved_at,
            elapsed_seconds=time.time() - started,
            error_class="UNAVAILABLE",
            error_message=str(exc),
        )
    except json.JSONDecodeError as exc:
        return HTTPResult(
            ok=False,
            status=None,
            payload=None,
            retrieved_at=retrieved_at,
            elapsed_seconds=time.time() - started,
            error_class="MALFORMED_RESPONSE",
            error_message=f"Invalid JSON: {exc}",
        )
    except TimeoutError as exc:
        return HTTPResult(
            ok=False,
            status=None,
            payload=None,
            retrieved_at=retrieved_at,
            elapsed_seconds=time.time() - started,
            error_class="TIMEOUT",
            error_message=f"{type(exc).__name__}: {exc}",
        )
    except Exception as exc:
        return HTTPResult(
            ok=False,
            status=None,
            payload=None,
            retrieved_at=retrieved_at,
            elapsed_seconds=time.time() - started,
            error_class="TECHNICAL_ERROR",
            error_message=f"{type(exc).__name__}: {exc}",
        )