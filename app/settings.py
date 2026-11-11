from __future__ import annotations

from urllib.parse import unquote

from flask import Request
from werkzeug.wrappers import Response

from app import timezones
from app.types import Hemisphere, IslandSettings, TimezoneSource

TIMEZONE_COOKIE = "cc_timezone"
HEMISPHERE_COOKIE = "cc_hemisphere"
COOKIE_MAX_AGE = 60 * 60 * 24 * 365
# Set by Vercel's edge from the visitor's IP; used as a first guess until the browser reports its zone.
IP_TIMEZONE_HEADER = "X-Vercel-IP-Timezone"
# Tropical islands are a coin flip, so only default to Southern for zones clearly south of the equator.
SOUTHERN_LATITUDE = -10.0


def parse_hemisphere(value: str | None) -> Hemisphere | None:
    normalized = (value or "").strip().lower()
    if normalized in ("northern", "north", "n"):
        return Hemisphere.NORTHERN
    if normalized in ("southern", "south", "s"):
        return Hemisphere.SOUTHERN
    return None


def parse_int(value: str | None, low: int, high: int) -> int | None:
    try:
        number = int(value or "")
    except ValueError:
        return None
    return number if low <= number <= high else None


def default_hemisphere(timezone: str) -> Hemisphere:
    latitude = timezones.latitude(timezone)
    return Hemisphere.SOUTHERN if latitude is not None and latitude < SOUTHERN_LATITUDE else Hemisphere.NORTHERN


def resolve(request: Request) -> IslandSettings:
    values = request.values
    cookie_timezone = request.cookies.get(TIMEZONE_COOKIE)
    candidates: tuple[tuple[TimezoneSource, str | None], ...] = (
        ("query", values.get("timezone") or values.get("tz")),
        ("cookie", unquote(cookie_timezone) if cookie_timezone else None),
        ("ip", request.headers.get(IP_TIMEZONE_HEADER)),
    )
    source: TimezoneSource = "fallback"
    timezone = "UTC"
    invalid: str | None = None
    for candidate_source, value in candidates:
        if value and timezones.is_known(value):
            source, timezone = candidate_source, value
            break
        if value and candidate_source != "ip" and invalid is None:
            invalid = value

    query_hemisphere = parse_hemisphere(values.get("hemisphere"))
    hemisphere = (query_hemisphere or parse_hemisphere(request.cookies.get(HEMISPHERE_COOKIE))
                  or default_hemisphere(timezone))
    planning = values.get("when") != "now"
    now = timezones.now_in(timezone)
    return IslandSettings(
        hemisphere=hemisphere,
        timezone=timezone,
        timezone_label=timezones.label(timezone),
        timezone_source=source,
        timezone_invalid=invalid,
        now=now,
        offset_minutes=timezones.offset_minutes(now),
        planned_month=parse_int(values.get("month"), 1, 12) if planning else None,
        planned_hour=parse_int(values.get("hour"), 0, 23) if planning else None,
        persist_timezone=source == "query",
        persist_hemisphere=query_hemisphere is not None,
    )


def persist(response: Response, settings: IslandSettings) -> None:
    if settings.persist_timezone:
        response.set_cookie(TIMEZONE_COOKIE, settings.timezone, max_age=COOKIE_MAX_AGE, samesite="Lax")
    if settings.persist_hemisphere:
        response.set_cookie(HEMISPHERE_COOKIE, settings.hemisphere.value, max_age=COOKIE_MAX_AGE, samesite="Lax")


def query_params(settings: IslandSettings) -> dict[str, str]:
    """Settings that arrived in the URL, so links can carry them when cookies aren't available."""
    params: dict[str, str] = {}
    if settings.persist_hemisphere:
        params["hemisphere"] = settings.hemisphere.value
    if settings.persist_timezone:
        params["timezone"] = settings.timezone
    if settings.planned_month is not None:
        params["month"] = str(settings.planned_month)
    if settings.planned_hour is not None:
        params["hour"] = str(settings.planned_hour)
    return params
