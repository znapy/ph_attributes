"""Helper functions and structures for the project."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

def to_datetime(value: int, tz: ZoneInfo) -> datetime:
    """Get current datetime from unixtime."""
    return datetime.fromtimestamp(value, tz=tz)

def to_unixtime(value: datetime) -> int:
    """Get current unixtime from datetime."""
    return int(value.timestamp())


@dataclass
class PeriodWithUTC:
    """Period with UTC."""
    start: datetime
    end: datetime
    path: Path
    timezone: ZoneInfo  # For time in filename ("path" property).

    @classmethod
    def system_zone(cls) -> ZoneInfo:
        """System zone will be replaced from config."""
        return ZoneInfo("Etc/UTC")

    def __post_init__(self):
        self.start = self.start.replace(tzinfo=self.system_zone())
        self.end = self.end.replace(tzinfo=self.system_zone())

@dataclass
class FileStatWithUTC:
    """File stat with UTC."""
    path: Path
    mtime: datetime

    def __init__(self, path: Path, mtime: datetime | None = None):
        self.path = path
        if mtime is None:
            self.mtime = to_datetime(path.stat().st_mtime, self.system_zone())
        else:
            self.mtime = mtime.replace(tzinfo=self.system_zone())

    @classmethod
    def system_zone(cls) -> ZoneInfo:
        """System zone will be replaced from config."""
        return ZoneInfo("Etc/UTC")

