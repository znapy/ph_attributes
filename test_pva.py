"""Pytests for the pva module."""

from datetime import datetime
import os
from pathlib import Path
from pytest_mock import MockFixture
import tempfile
from zoneinfo import ZoneInfo

from config_example import Period, SYSTEM_ZONE
import pva


def _configure_tmp_dir(path: Path, subdir_name: str, filename: str
                       ) -> tuple[list[Period], Path]:
    subdir = path / subdir_name
    subdir.mkdir(parents=True)
    filepath = subdir / filename
    with open(filepath, 'w') as f:
        f.write('')
    os.utime(filepath, times=(1605270645, 1605270645))  # 2020-11-13 12:30:45

    return ([
        Period(
            start=datetime(2010, 1, 1),
            end=datetime(2024, 12, 31, 23, 59, 59),
            path=path,
            timezone=ZoneInfo("Europe/Moscow"),
        ),
        Period(
            start=datetime(2022, 2, 24),
            end=datetime(2024, 12, 31, 23, 59, 59),
            path=subdir,
            timezone=ZoneInfo("Etc/UTC"),
        ),
    ], filepath)

def _check_mtime(mocker: MockFixture, filepath: Path, unix_time: int,
                 periods: list[Period]) -> None:
    """Check mtime of the file."""
    mocker.patch("pva.rules.PERIODS", periods)
    mocker.patch("pva.rules.SYSTEM_ZONE", SYSTEM_ZONE)
    mocker.patch("pva.get_args", lambda: mocker.MagicMock(change_files=True))

    assert int(filepath.stat().st_mtime) != unix_time
    pva.main()
    assert int(filepath.stat().st_mtime) == unix_time


def test_main__path_with_space(mocker: MockFixture) -> None:
    """Test main function - scenario for a file with date and time."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        periods, filepath = _configure_tmp_dir(
            Path(tmp_dir), "name with spaces", '20231231_191530.jpg')
        unix_time = 1704050130  # equivalent filename: 2023-12-31 19:15:30

        _check_mtime(mocker, filepath, unix_time, periods)

def test_main__filename_and_dir_with_date(mocker: MockFixture) -> None:
    """
    Test main function - scenario for a file (date) and dir (year-month).

    In this conflict rules the filename rule is more important.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        periods, filepath = _configure_tmp_dir(
            Path(tmp_dir), "2023-12", '2023-12-31.jpg')
        unix_time = 1704025845  # 2023-12-31 12:30:45

        _check_mtime(mocker, filepath, unix_time, periods)
