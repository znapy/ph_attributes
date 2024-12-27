"""Periods example."""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import helpers

SYSTEM_ZONE = ZoneInfo("Etc/UTC")

class Period(helpers.PeriodWithUTC):
    """Period with system time zone."""
    @classmethod
    def system_zone(cls) -> ZoneInfo:
        """System zone from config."""
        return SYSTEM_ZONE


# File in path is appropriate for Period if date from rule between start-end
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
