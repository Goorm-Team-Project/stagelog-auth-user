from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

import requests
from contracts.internal_api_contracts import (
    AUTH_INTERNAL_USER_EXP,
    AUTH_INTERNAL_USERS_BATCH_GET,
    CORE_INTERNAL_BOOKMARK_FAVORITE_COUNTS,
    EVENTS_INTERNAL_BATCH_SUMMARY,
    EVENTS_INTERNAL_EXISTS,
    EVENTS_INTERNAL_SUMMARY,
)
from django.conf import settings


class InternalApiError(Exception):
    pass


def _enabled() -> bool:
    return bool(getattr(settings, "USE_INTERNAL_SERVICE_API", False))


def _request_json(
    method: str,
    url: str,
    *,
    payload: Optional[Dict[str, Any]] = None,
    timeout: tuple[float, float] = (0.3, 0.7),
) -> Dict[str, Any]:
    try:
        resp = requests.request(method, url, json=payload, timeout=timeout)
    except requests.RequestException as exc:
        raise InternalApiError(str(exc)) from exc

    if resp.status_code >= 400:
        raise InternalApiError(f"{resp.status_code}: {resp.text[:200]}")

    try:
        return resp.json()
    except ValueError as exc:
        raise InternalApiError("invalid json response") from exc


def get_users_batch(user_ids: Iterable[int]) -> Dict[int, str]:
    if not _enabled():
        raise InternalApiError("internal api disabled")

    base = getattr(settings, "AUTH_INTERNAL_BASE_URL", "").rstrip("/")
    if not base:
        raise InternalApiError("AUTH_INTERNAL_BASE_URL is empty")

    ids = sorted({int(uid) for uid in user_ids if uid is not None})
    if not ids:
        return {}

    data = _request_json("POST", f"{base}{AUTH_INTERNAL_USERS_BATCH_GET}", payload={"user_ids": ids})
    rows = data.get("users") or []
    return {int(row["user_id"]): row.get("nickname") for row in rows if row.get("user_id") is not None}


def apply_user_exp(user_id: int, policy: str) -> Dict[str, Any]:
    if not _enabled():
        raise InternalApiError("internal api disabled")

    base = getattr(settings, "AUTH_INTERNAL_BASE_URL", "").rstrip("/")
    if not base:
        raise InternalApiError("AUTH_INTERNAL_BASE_URL is empty")

    return _request_json(
        "POST",
        f"{base}{AUTH_INTERNAL_USER_EXP.format(user_id=int(user_id))}",
        payload={"policy": policy},
    )


def event_exists(event_id: int) -> bool:
    if not _enabled():
        raise InternalApiError("internal api disabled")

    base = getattr(settings, "EVENTS_INTERNAL_BASE_URL", "").rstrip("/")
    if not base:
        raise InternalApiError("EVENTS_INTERNAL_BASE_URL is empty")

    data = _request_json("GET", f"{base}{EVENTS_INTERNAL_EXISTS.format(event_id=int(event_id))}")
    return bool(data.get("exists"))


def get_event_summary(event_id: int) -> Dict[str, Any]:
    if not _enabled():
        raise InternalApiError("internal api disabled")

    base = getattr(settings, "EVENTS_INTERNAL_BASE_URL", "").rstrip("/")
    if not base:
        raise InternalApiError("EVENTS_INTERNAL_BASE_URL is empty")

    return _request_json("GET", f"{base}{EVENTS_INTERNAL_SUMMARY.format(event_id=int(event_id))}")


def get_events_batch(event_ids: Iterable[int]) -> Dict[int, Dict[str, Any]]:
    if not _enabled():
        raise InternalApiError("internal api disabled")

    base = getattr(settings, "EVENTS_INTERNAL_BASE_URL", "").rstrip("/")
    if not base:
        raise InternalApiError("EVENTS_INTERNAL_BASE_URL is empty")

    ids = sorted({int(eid) for eid in event_ids if eid is not None})
    if not ids:
        return {}

    data = _request_json("POST", f"{base}{EVENTS_INTERNAL_BATCH_SUMMARY}", payload={"event_ids": ids})
    rows = data.get("events") or []
    return {int(row["event_id"]): row for row in rows if row.get("event_id") is not None}


def get_favorite_counts(event_ids: Iterable[int]) -> Dict[int, int]:
    if not _enabled():
        raise InternalApiError("internal api disabled")

    base = getattr(settings, "CORE_INTERNAL_BASE_URL", "").rstrip("/")
    if not base:
        raise InternalApiError("CORE_INTERNAL_BASE_URL is empty")

    ids = sorted({int(eid) for eid in event_ids if eid is not None})
    if not ids:
        return {}

    data = _request_json(
        "POST",
        f"{base}{CORE_INTERNAL_BOOKMARK_FAVORITE_COUNTS}",
        payload={"event_ids": ids},
    )
    rows: List[Dict[str, Any]] = data.get("counts") or []
    return {int(row["event_id"]): int(row.get("favorite_count") or 0) for row in rows if row.get("event_id") is not None}
