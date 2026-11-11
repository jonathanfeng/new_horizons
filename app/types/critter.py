from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CritterKind(str, Enum):
    FISH = "fish"
    BUGS = "bugs"
    SEA_CREATURES = "sea_creatures"


class Hemisphere(str, Enum):
    NORTHERN = "Northern"
    SOUTHERN = "Southern"


@dataclass(frozen=True, slots=True)
class Critter:
    kind: CritterKind
    number: int
    name: str
    price: int
    # Active hours for each Northern Hemisphere month (index 0 is January); empty when out of season.
    hours_by_month: tuple[frozenset[int], ...]
    min_catches: int
    location: str | None = None
    shadow: str | None = None
    speed: str | None = None
    weather: str | None = None


@dataclass(frozen=True, slots=True)
class FilterChip:
    value: str
    label: str


@dataclass(frozen=True, slots=True)
class KindInfo:
    kind: CritterKind
    endpoint: str
    title: str
    page_title: str
    cta: str
    singular: str
    plural: str
    icon: str
    seller: str | None
    filters: tuple[FilterChip, ...]


@dataclass(frozen=True, slots=True)
class ShadowArt:
    rx: float
    ry: float
    fin: bool


@dataclass(frozen=True, slots=True)
class Badge:
    tone: str
    icon: str
    label: str
    title: str | None = None


@dataclass(frozen=True, slots=True)
class CritterStatus:
    critter: Critter
    available: bool
    in_season: bool
    is_new: bool
    is_leaving: bool
    months: frozenset[int]
    months_label: str
    # Hours for the month being shown, or for the month the critter returns in when out of season.
    hours: frozenset[int]
    hours_label: str
    schedule: tuple[tuple[str, str], ...]
    months_left: int
    next_label: str | None
    until_label: str | None
    meta: str
    tags: tuple[str, ...]
    badges: tuple[Badge, ...]
    shadow: ShadowArt | None
    speed_level: int | None
    seller_price: int | None


@dataclass(frozen=True, slots=True)
class KindSummary:
    info: KindInfo
    total: int
    available: int
    new: tuple[CritterStatus, ...]
    leaving: tuple[CritterStatus, ...]
    top: tuple[CritterStatus, ...]
