from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from app.types.critter import Hemisphere

TimezoneSource = Literal["query", "cookie", "ip", "fallback"]
DetectMode = Literal["required", "verify"]


@dataclass(frozen=True, slots=True)
class TimezoneOption:
    value: str
    label: str


@dataclass(frozen=True, slots=True)
class TimezoneGroup:
    label: str
    options: tuple[TimezoneOption, ...]


@dataclass(frozen=True, slots=True)
class IslandSettings:
    hemisphere: Hemisphere
    timezone: str
    timezone_label: str
    timezone_source: TimezoneSource
    # A time zone we were given but couldn't recognize (shown to the user instead of auto-detecting).
    timezone_invalid: str | None
    now: datetime
    offset_minutes: int
    planned_month: int | None
    planned_hour: int | None
    persist_timezone: bool
    persist_hemisphere: bool

    @property
    def planning(self) -> bool:
        return self.planned_month is not None or self.planned_hour is not None

    @property
    def month(self) -> int:
        return self.planned_month if self.planned_month is not None else self.now.month

    @property
    def hour(self) -> int:
        return self.planned_hour if self.planned_hour is not None else self.now.hour

    @property
    def detect_mode(self) -> DetectMode | None:
        if self.timezone_source == "ip":
            return "verify"
        if self.timezone_source == "fallback" and self.timezone_invalid is None:
            return "required"
        return None
