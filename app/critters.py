"""Critter data and availability rules.

Each ``app/data/<kind>.csv`` row is one Critterpedia entry with Northern Hemisphere months. A month cell is
``-`` when out of season, ``1`` when the row's default ``hours`` apply, or an hours spec for that month.
Hours specs are 24-hour windows with an exclusive end (``16 - 9`` is 4 PM to 9 AM) joined with ``&``, or
``All day``. The Southern Hemisphere is the Northern one shifted by six months.
"""
from __future__ import annotations

import csv
from functools import cache
from pathlib import Path

from app.types import (
    Badge,
    Critter,
    CritterKind,
    CritterStatus,
    FilterChip,
    Hemisphere,
    IslandSettings,
    KindInfo,
    KindSummary,
    ShadowArt,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
MONTH_KEYS = ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec")
MONTH_ABBRS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
MONTH_NAMES = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)
ALL_HOURS = frozenset(range(24))

FISH_SHADOW_LABELS = {1: "Tiny", 2: "Small", 3: "Medium", 4: "Large", 5: "Very large", 6: "Huge"}
SEA_SHADOW_SIZES = {"Tiny": 1, "Small": 2, "Medium": 3, "Large": 4, "Very large": 5}
SPEED_LEVELS = {"Stationary": 0, "Very slow": 1, "Slow": 2, "Medium": 3, "Fast": 4, "Very fast": 5}
SPEED_TAGS = {"Stationary": "stationary", "Very slow": "slow", "Slow": "slow", "Medium": "medium",
              "Fast": "fast", "Very fast": "fast"}

KINDS: dict[CritterKind, KindInfo] = {
    CritterKind.FISH: KindInfo(
        kind=CritterKind.FISH, endpoint="fish", title="Fish", singular="fish", plural="fish", icon="fish",
        tagline="Cast a line in rivers, ponds, the sea, and off the pier.", seller="C.J.",
        filters=(FilterChip("river", "River"), FilterChip("pond", "Pond"), FilterChip("sea", "Sea"),
                 FilterChip("pier", "Pier")),
    ),
    CritterKind.BUGS: KindInfo(
        kind=CritterKind.BUGS, endpoint="bugs", title="Bugs", singular="bug", plural="bugs", icon="bug",
        tagline="Net them on flowers, trees, rocks, and riverbanks.", seller="Flick",
        filters=(FilterChip("flying", "Flying"), FilterChip("trees", "Trees"), FilterChip("flowers", "Flowers"),
                 FilterChip("ground", "Ground"), FilterChip("water", "Water & beach"), FilterChip("other", "Other")),
    ),
    CritterKind.SEA_CREATURES: KindInfo(
        kind=CritterKind.SEA_CREATURES, endpoint="sea_creatures", title="Sea Creatures", singular="sea creature",
        plural="sea creatures", icon="shell", tagline="Put on a wet suit and dive wherever you spot bubbles.",
        seller=None,
        filters=(FilterChip("stationary", "Stationary"), FilterChip("slow", "Slow"), FilterChip("medium", "Medium"),
                 FilterChip("fast", "Fast")),
    ),
}


def parse_hours(spec: str) -> frozenset[int]:
    spec = spec.strip()
    if spec.lower() == "all day":
        return ALL_HOURS
    hours: set[int] = set()
    for window in spec.split("&"):
        start, end = (int(part) for part in window.split("-"))
        if not (0 <= start <= 23 and 0 <= end <= 23) or start == end:
            raise ValueError(f"Invalid hours window {window.strip()!r}")
        hours.update(range(start, end) if start < end else (*range(start, 24), *range(end)))
    return frozenset(hours)


def _month_hours(cell: str, default: frozenset[int]) -> frozenset[int]:
    cell = cell.strip()
    if cell == "-":
        return frozenset()
    return default if cell == "1" else parse_hours(cell)


@cache
def catalog(kind: CritterKind) -> tuple[Critter, ...]:
    with (DATA_DIR / f"{kind.value}.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    entries = []
    for row in rows:
        default_hours = parse_hours(row["hours"])
        entries.append(Critter(
            kind=kind,
            number=int(row["number"]),
            name=row["name"].strip(),
            price=int(row["price"]),
            hours_by_month=tuple(_month_hours(row[key], default_hours) for key in MONTH_KEYS),
            min_catches=int(row["min_catches"]),
            location=row.get("location") or None,
            shadow=row.get("shadow") or None,
            speed=row.get("speed") or None,
            weather=row.get("weather") or None,
        ))
    return tuple(sorted(entries, key=lambda critter: critter.number))


def northern_month(month: int, hemisphere: Hemisphere) -> int:
    return month if hemisphere is Hemisphere.NORTHERN else (month + 5) % 12 + 1


def hours_in(critter: Critter, hemisphere: Hemisphere, month: int) -> frozenset[int]:
    return critter.hours_by_month[northern_month(month, hemisphere) - 1]


def active_months(critter: Critter, hemisphere: Hemisphere) -> frozenset[int]:
    return frozenset(month for month in range(1, 13) if hours_in(critter, hemisphere, month))


def is_available(critter: Critter, hemisphere: Hemisphere, month: int, hour: int) -> bool:
    return hour in hours_in(critter, hemisphere, month)


def format_hour(hour: int) -> str:
    return f"{hour % 12 or 12} {'AM' if hour < 12 else 'PM'}"


def _runs(values: frozenset[int], size: int) -> list[tuple[int, int]]:
    """Circular runs of consecutive values as ``(start, length)``, ordered by start."""
    if len(values) == size:
        return [(0, size)]
    runs = []
    for value in sorted(values):
        if (value - 1) % size in values:
            continue
        length = 1
        while (value + length) % size in values:
            length += 1
        runs.append((value, length))
    return runs


def hours_label(hours: frozenset[int]) -> str:
    if hours == ALL_HOURS:
        return "All day"
    return " & ".join(f"{format_hour(start)} – {format_hour((start + length) % 24)}"
                      for start, length in _runs(hours, 24))


def months_label(months: frozenset[int]) -> str:
    if len(months) == 12:
        return "All year"
    parts = []
    for start, length in _runs(frozenset(month - 1 for month in months), 12):
        first, last = MONTH_ABBRS[start], MONTH_ABBRS[(start + length - 1) % 12]
        parts.append(first if length == 1 else f"{first} – {last}")
    return ", ".join(parts)


def _next_month(months: frozenset[int], month: int) -> int:
    return next(candidate for step in range(1, 13) if (candidate := (month - 1 + step) % 12 + 1) in months)


def _next_hour(hours: frozenset[int], hour: int, *, active: bool) -> int:
    return next(candidate for step in range(1, 25) if ((candidate := (hour + step) % 24) in hours) == active)


def _months_left(months: frozenset[int], month: int) -> int:
    if month not in months:
        return 0
    if len(months) == 12:
        return 12
    count = 0
    while (month - 1 + count) % 12 + 1 in months:
        count += 1
    return count


def _schedule(critter: Critter, hemisphere: Hemisphere) -> tuple[tuple[str, str], ...]:
    groups: dict[frozenset[int], list[int]] = {}
    for month in range(1, 13):
        if hours := hours_in(critter, hemisphere, month):
            groups.setdefault(hours, []).append(month)
    if len(groups) < 2:
        return ()
    ordered = sorted(groups.items(), key=lambda item: item[1][0])
    return tuple((months_label(frozenset(months)), hours_label(hours)) for hours, months in ordered)


def _tags(critter: Critter) -> tuple[str, ...]:
    if critter.kind is CritterKind.SEA_CREATURES:
        return (SPEED_TAGS[critter.speed],) if critter.speed in SPEED_TAGS else ()
    location = (critter.location or "").lower()
    if critter.kind is CritterKind.FISH:
        tags = [tag for tag in ("river", "pond", "pier") if tag in location]
        if location.startswith("sea"):
            tags.append("sea")
        return tuple(tags)
    tags = []
    if location.startswith("flying"):
        tags.append("flying")
    if "tree" in location or "stump" in location:
        tags.append("trees")
    if "flower" in location:
        tags.append("flowers")
    if any(word in location for word in ("ground", "snowball", "rocks and bushes", "hitting rocks")):
        tags.append("ground")
    if any(word in location for word in ("river", "pond", "water", "shore", "beach")):
        tags.append("water")
    return tuple(tags) or ("other",)


def _fish_shadow(critter: Critter) -> tuple[str, int | None, bool]:
    size, _, fin = (critter.shadow or "").partition(" ")
    if size == "narrow":
        return "Narrow", None, False
    return FISH_SHADOW_LABELS[int(size)], int(size), fin == "fin"


def _shadow_art(critter: Critter) -> ShadowArt | None:
    if critter.kind is CritterKind.FISH:
        _, size, fin = _fish_shadow(critter)
        if size is None:
            return ShadowArt(rx=25.0, ry=3.6, fin=False)
        rx = 8 + 3.4 * size
        return ShadowArt(rx=round(rx, 1), ry=round(rx * 0.42, 1), fin=fin)
    if critter.kind is CritterKind.SEA_CREATURES and critter.shadow in SEA_SHADOW_SIZES:
        rx = 8.0 + 4 * SEA_SHADOW_SIZES[critter.shadow]
        return ShadowArt(rx=rx, ry=round(rx * 0.42, 1), fin=False)
    return None


def _meta(critter: Critter) -> str:
    if critter.kind is CritterKind.FISH:
        label, _, fin = _fish_shadow(critter)
        return f"{critter.location} · {label} shadow{' with fin' if fin else ''}"
    if critter.kind is CritterKind.BUGS:
        return critter.location or ""
    return f"{critter.shadow} shadow · {critter.speed}"


def _badges(critter: Critter, month: int, *, is_new: bool, is_leaving: bool) -> tuple[Badge, ...]:
    info = KINDS[critter.kind]
    badges = []
    if is_new:
        badges.append(Badge("new", "sparkles", "New this month"))
    if is_leaving:
        badges.append(Badge("leaving", "hourglass", f"Leaves after {MONTH_ABBRS[month - 1]}",
                            "Last month of its season, so catch it before the month ends"))
    if critter.weather == "rain only":
        badges.append(Badge("weather", "cloud-rain", "Rain only", "Only appears while it's raining"))
    elif "rain" in (critter.location or "").lower():
        badges.append(Badge("weather", "cloud-rain", "Rain or snow", "Only appears while it's raining or snowing"))
    elif critter.weather == "no rain":
        badges.append(Badge("muted", "sun", "No rain", "Hides while it's raining"))
    if critter.min_catches:
        badges.append(Badge("muted", "lock", f"{critter.min_catches}+ catches",
                            f"Only spawns after you've caught {critter.min_catches} {info.plural} in total"))
    return tuple(badges)


def status(critter: Critter, hemisphere: Hemisphere, month: int, hour: int) -> CritterStatus:
    months = active_months(critter, hemisphere)
    in_season = month in months
    all_year = len(months) == 12
    this_month = hours_in(critter, hemisphere, month)
    available = hour in this_month
    shown_month = month if in_season else _next_month(months, month)
    shown_hours = hours_in(critter, hemisphere, shown_month)
    is_new = in_season and not all_year and (month - 2) % 12 + 1 not in months
    is_leaving = in_season and not all_year and month % 12 + 1 not in months

    next_label = until_label = None
    if available:
        if this_month != ALL_HOURS:
            until_label = f"Until {format_hour(_next_hour(this_month, hour, active=False))}"
    elif in_season:
        next_label = f"Back at {format_hour(_next_hour(this_month, hour, active=True))}"
    else:
        next_label = f"Returns in {MONTH_NAMES[shown_month - 1]}"

    seller = KINDS[critter.kind].seller
    return CritterStatus(
        critter=critter,
        available=available,
        in_season=in_season,
        is_new=is_new,
        is_leaving=is_leaving,
        months=months,
        months_label=months_label(months),
        hours=shown_hours,
        hours_label=hours_label(shown_hours),
        schedule=_schedule(critter, hemisphere),
        months_left=_months_left(months, month),
        next_label=next_label,
        until_label=until_label,
        meta=_meta(critter),
        tags=_tags(critter),
        badges=_badges(critter, month, is_new=is_new, is_leaving=is_leaving),
        shadow=_shadow_art(critter),
        speed_level=SPEED_LEVELS.get(critter.speed or ""),
        seller_price=critter.price * 3 // 2 if seller else None,
    )


def statuses(kind: CritterKind, settings: IslandSettings) -> tuple[CritterStatus, ...]:
    items = (status(critter, settings.hemisphere, settings.month, settings.hour) for critter in catalog(kind))
    return tuple(sorted(items, key=lambda item: (not item.available, -item.critter.price, item.critter.number)))


def summarize(kind: CritterKind, items: tuple[CritterStatus, ...]) -> KindSummary:
    available = [item for item in items if item.available]
    by_price = sorted(items, key=lambda item: -item.critter.price)
    return KindSummary(
        info=KINDS[kind],
        total=len(items),
        available=len(available),
        new=tuple(item for item in by_price if item.is_new),
        leaving=tuple(item for item in by_price if item.is_leaving),
        top=tuple(sorted(available, key=lambda item: -item.critter.price)[:3]),
    )
