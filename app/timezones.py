from __future__ import annotations

import re
from datetime import datetime, timezone
from functools import cache, lru_cache
from importlib import resources

import pytz

from app.types import TimezoneGroup, TimezoneOption

REGION_LABELS = {
    "Africa": "Africa",
    "America": "Americas",
    "Antarctica": "Antarctica",
    "Arctic": "Arctic",
    "Asia": "Asia",
    "Atlantic": "Atlantic",
    "Australia": "Australia",
    "Europe": "Europe",
    "Indian": "Indian Ocean",
    "Pacific": "Pacific",
    "Canada": "Canada",
    "US": "United States",
}
OTHER_REGION = "Other"


def is_known(name: str | None) -> bool:
    return bool(name) and name in pytz.all_timezones_set


def now_in(name: str) -> datetime:
    return datetime.now(pytz.timezone(name))


def offset_minutes(moment: datetime) -> int:
    offset = moment.utcoffset()
    return int(offset.total_seconds() // 60) if offset is not None else 0


def format_offset(minutes: int) -> str:
    hours, mins = divmod(abs(minutes), 60)
    return f"UTC{'+' if minutes >= 0 else '−'}{hours:02d}:{mins:02d}"


def clock_time(moment: datetime) -> str:
    return f"{moment.hour % 12 or 12}:{moment.minute:02d} {'AM' if moment.hour < 12 else 'PM'}"


def clock_date(moment: datetime) -> str:
    return f"{moment.strftime('%a, %b')} {moment.day}"


def place_label(name: str) -> str:
    parts = name.replace("_", " ").split("/")
    if len(parts) == 3:
        return f"{parts[2]}, {parts[1]}"
    return parts[-1]


def label(name: str, at: datetime | None = None) -> str:
    if "/" not in name:
        return name
    moment = (at or datetime.now(timezone.utc)).astimezone(pytz.timezone(name))
    return f"{place_label(name)} ({format_offset(offset_minutes(moment))})"


@lru_cache(maxsize=2)
def _groups(utc_hour: str) -> tuple[TimezoneGroup, ...]:
    at = datetime.now(timezone.utc)
    grouped: dict[str, list[TimezoneOption]] = {}
    for name in pytz.common_timezones:
        region = REGION_LABELS.get(name.split("/")[0], OTHER_REGION) if "/" in name else OTHER_REGION
        grouped.setdefault(region, []).append(TimezoneOption(name, label(name, at)))
    order = (*REGION_LABELS.values(), OTHER_REGION)
    return tuple(
        TimezoneGroup(region, tuple(sorted(options, key=lambda option: option.label)))
        for region in order
        if (options := grouped.get(region))
    )


def options(selected: str) -> tuple[TimezoneGroup, ...]:
    groups = _groups(datetime.now(timezone.utc).strftime("%Y%m%d%H"))
    if selected in pytz.common_timezones_set:
        return groups
    return (TimezoneGroup("Your time zone", (TimezoneOption(selected, label(selected)),)), *groups)


def _latitude(coordinates: str) -> float:
    match = re.match(r"([+-])(\d{2})(\d{2})(\d{2})?", coordinates)
    if match is None:
        raise ValueError(f"Bad ISO 6709 coordinates {coordinates!r}")
    sign, degrees, minutes, seconds = match.groups()
    value = int(degrees) + int(minutes) / 60 + int(seconds or 0) / 3600
    return value if sign == "+" else -value


@cache
def _latitudes() -> dict[str, float]:
    latitudes: dict[str, float] = {}
    zone_tab = resources.files("pytz").joinpath("zoneinfo", "zone.tab").read_text(encoding="utf-8")
    for line in zone_tab.splitlines():
        if line.strip() and not line.startswith("#"):
            _, coordinates, name, *_ = line.split("\t")
            latitudes[name] = _latitude(coordinates)
    return latitudes


def latitude(name: str) -> float | None:
    latitudes = _latitudes()
    if name in latitudes:
        return latitudes[name]
    # Legacy aliases (e.g. America/Buenos_Aires) aren't in zone.tab; match on the city instead.
    city = name.rsplit("/", 1)[-1]
    return next((value for zone, value in latitudes.items() if zone.rsplit("/", 1)[-1] == city), None)
