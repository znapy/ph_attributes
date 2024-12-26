"""Helper functions and structures for the project."""

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

def to_datetime(value: int, tz: ZoneInfo) -> datetime:
    """Get current datetime from unixtime."""
    return datetime.fromtimestamp(value, tz=tz)

def to_unixtime(value: datetime) -> int:
    """Get current unixtime from datetime."""
    return int(value.timestamp())
