"""Pytests for the pva module."""

from datetime import datetime
from pathlib import Path
from pytest_mock import MockFixture
import rules
from zoneinfo import ZoneInfo

# how to use the period-example.py module instead of the periods.py module
from periods_example import PERIODS, SYSTEM_ZONE, timezone_for_date


def test_date_n_time(mocker: MockFixture) -> None:
    """Test rule 'date_n_time'."""
    mocker.patch("rules.PERIODS", PERIODS)
    mocker.patch("rules.timezone_for_date", timezone_for_date)
    moscow = ZoneInfo("Europe/Moscow")

    assert rules.rule_date_n_time(rules.FileStat(
        path=Path("/a/b/20101231_161530.jpg"),
        mtime=datetime(2010, 12, 31, 16, 15, 30, tzinfo=moscow
                       ).astimezone(SYSTEM_ZONE))
        ) is None

    # UTC is only for directory "/a/b/2022", here is Moscow time
    assert rules.rule_date_n_time(rules.FileStat(
        path=Path("/a/b/20240101_010100.jpg"),
        mtime=datetime(2024, 1, 1, 1, 1, 0, tzinfo=moscow
                       ).astimezone(SYSTEM_ZONE))
        ) is None

    assert rules.rule_date_n_time(rules.FileStat(
        path=Path("/a/b/2022/20220101_010100.jpg"),
        mtime=datetime(2022, 1, 1, 1, 1, 0, tzinfo=moscow
                       ).astimezone(SYSTEM_ZONE))
        ) is None

    assert rules.rule_date_n_time(rules.FileStat(
        path=Path("/a/b/2022/20220301_010100.jpg"),
        mtime=datetime(2022, 3, 1, 1, 1, 0))
        ) is None

    assert rules.rule_date_n_time(rules.FileStat(
        path=Path("/a/b/2022/20220201_010100.jpg"),
        mtime=datetime(2024, 12, 31, 1, 1, 0))
        ) == datetime(2022, 2, 1, 1, 1, 0, tzinfo=moscow)

    assert rules.rule_date_n_time(rules.FileStat(
        path=Path("/a/b/2022/20220301_010100.jpg"),
        mtime=datetime(2024, 12, 31, 1, 1, 0))
        ) == datetime(2022, 3, 1, 1, 1, 0, tzinfo=SYSTEM_ZONE)
