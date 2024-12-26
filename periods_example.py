"""Periods example."""

import dataclasses
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

SYSTEM_ZONE = ZoneInfo("Etc/UTC")

@dataclasses.dataclass
class Period:
    """Period."""
    start: datetime
    end: datetime
    path: Path
    timezone: ZoneInfo  # For time in filename ("path" property).

    def __post_init__(self):
        self.start = self.start.replace(tzinfo=SYSTEM_ZONE)
        self.end = self.end.replace(tzinfo=SYSTEM_ZONE)


PERIODS: list[Period] = [
    Period(
        start=datetime(2010, 1, 1),
        end=datetime(2024, 12, 31, 23, 59, 59),
        path=Path("/a/b/"),
        timezone=ZoneInfo("Europe/Moscow"),
    ),
    Period(
        start=datetime(2022, 2, 24),
        end=datetime(2024, 12, 31, 23, 59, 59),
        path=Path("/a/b/2022"),
        timezone=ZoneInfo("Etc/UTC"),
    ),
]

def timezone_for_date(date_n_time: datetime, path: Path) -> ZoneInfo:
    """Get timezone for period."""
    for period in reversed(PERIODS):
        if not path.parent.is_relative_to(period.path):
            continue
        if period.start <= date_n_time.astimezone(SYSTEM_ZONE) \
                        <= period.end:
            return period.timezone
    return ZoneInfo("Etc/UTC")
