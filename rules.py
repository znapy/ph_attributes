"""Rules to determine date and time of last modify."""

import dataclasses
from datetime import datetime
from pathlib import Path
from typing import Callable

from periods import PERIODS, SYSTEM_ZONE, timezone_for_date

YEARS = {year for period in PERIODS \
              for year in range(period.start.year, period.end.year + 1)}

@dataclasses.dataclass
class FileStat:
    """File stat."""

    path: Path
    mtime: datetime

    def __post_init__(self):
        self.mtime = self.mtime.replace(tzinfo=SYSTEM_ZONE)


# return (True, date_n_time) if the rule is applied and new datetime is needed
Rule = Callable[[FileStat], tuple[bool, datetime | None]]

def rule_date_n_time(file_stat: FileStat) -> tuple[bool, datetime | None]:
    """Example: '20150617_191500.jpg'."""
    stem = file_stat.path.stem
    if len(stem) != 15 \
            or stem[:8].isdigit() is False \
            or stem[8] != "_" \
            or stem[9:15].isdigit() is False:
        return (False, None)

    try:
        date_n_time = datetime.strptime(stem, "%Y%m%d_%H%M%S")
    except ValueError:
        return (False, None)

    if date_n_time.year not in YEARS:
        print(f"Year {date_n_time.year} for file '{file_stat.path}'"
              f" is not in years from periods.")
        return (True, None)

    timezone = timezone_for_date(date_n_time, file_stat.path)
    date_n_time = date_n_time.replace(tzinfo=timezone).astimezone(SYSTEM_ZONE)

    if date_n_time != file_stat.mtime:
        return (True, date_n_time)
    return (True, None)

# , IMG_20191127_194031.jpg, IMG_20200201_205103_1.jpg, VID-20200412-WA0000.mp4, VID_20200801_081626_LS.mp4, PXL_20230906_111508295.jpg, PXL_20230906_122117759.TS.mp4, PXL_20240102_112534347_exported_stabilized_1704194757966.gif
