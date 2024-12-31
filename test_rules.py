"""Pytests for the rules module."""

from datetime import datetime
from pathlib import Path
from pytest_mock import MockFixture

from config_example import PERIODS, SYSTEM_ZONE
import rules


def test__get_date_without_time() -> None:
    """Test _get_date_without_time function."""
    func = rules._get_date_without_time
    assert func("20201231") == datetime(2020, 12, 31)
    assert func("abc") is None
    assert func("2020-12-31", "%Y-%m-%d") == datetime(2020, 12, 31)
    assert func("2020-12-31 abc", "%Y-%m-%d") == datetime(2020, 12, 31)
    assert func("abc 2020-12-31", "%Y-%m-%d") is None
    assert func("2020.12.31", "%Y.%m.%d") == datetime(2020, 12, 31)
    assert func("2020-12 abc", "%Y-%m") == datetime(2020, 12, 1)
    assert func("2020 abc", "%Y") == datetime(2020, 1, 1)
    assert func("5000412") is None  # 4 is not a month


def test_date_n_time(mocker: MockFixture) -> None:
    """Test rule 'date_n_time'."""
    mocker.patch("rules.PERIODS", PERIODS)
    mocker.patch("rules.SYSTEM_ZONE", SYSTEM_ZONE)

    assert rules.rule_date_n_time(rules.FileStat(
        path=Path("/a/b/20101231_191530.jpg"),  # 19 in MSK is 16 in UTC
        mtime=datetime(2010, 12, 31, 16, 15, 30))
        ) == (True, None)

    # UTC is only for directory "/a/b/2022", here is Moscow time
    assert rules.rule_date_n_time(rules.FileStat(
        path=Path("/a/b/20240101_010100.jpg"),  # 01 in MSK is 22 in UTC
        mtime=datetime(2023, 12, 31, 22, 1, 0))
        ) == (True, None)

    assert rules.rule_date_n_time(rules.FileStat(
        path=Path("/a/b/2022/20220101_050100.jpg"),  # 05 in MSK is 02 in UTC
        mtime=datetime(2022, 1, 1, 2, 1, 0))
        ) == (True, None)

    # Filename in UTC, because "/a/b/2022" directory after 2022-02-24 (period)
    assert rules.rule_date_n_time(rules.FileStat(
        path=Path("/a/b/2022/20220301_010100.jpg"),
        mtime=datetime(2022, 3, 1, 1, 1, 0, tzinfo=SYSTEM_ZONE))
        ) == (True, None)

    # Incorrect mtime in 1st period
    assert rules.rule_date_n_time(rules.FileStat(
        path=Path("/a/b/2022/20220201_060100.jpg"),  # 06 in MSK is 03 in UTC
        mtime=datetime(2024, 12, 31, 1, 1, 0))
        ) == (True, datetime(2022, 2, 1, 3, 1, 0, tzinfo=SYSTEM_ZONE))

    # Incorrect mtime in 2nd period
    assert rules.rule_date_n_time(rules.FileStat(
        path=Path("/a/b/2022/20220301_010100.jpg"),  # in UTC by period
        mtime=datetime(2024, 12, 31, 1, 1, 0))
        ) == (True, datetime(2022, 3, 1, 1, 1, 0, tzinfo=SYSTEM_ZONE))

    # Incorrect filename
    assert rules.rule_date_n_time(rules.FileStat(
        path=Path("/a/b/2022/c.jpg"),
        mtime=datetime(2024, 12, 31, 1, 1, 0))
        ) == (False, None)

    # No date in filename
    assert rules.rule_date_n_time(rules.FileStat(
        path=Path("/a/b/12345678_123456.jpg"),
        mtime=datetime(2024, 12, 31, 1, 1, 0))
        ) == (False, None)

    # The year before periods
    assert rules.rule_date_n_time(rules.FileStat(
        path=Path("/a/b/19990301_010100.jpg"),
        mtime=datetime(2024, 12, 31, 1, 1, 0))
        ) == (True, None)

    assert rules.rule_date_n_time(rules.FileStat(
        path=Path("/a/b/IMG_20101231_191530_1.jpg"),  # 19 in MSK is 16 in UTC
        mtime=datetime(2010, 12, 31, 16, 15, 30))
        ) == (True, None)

    # Wrong prefix
    assert rules.rule_date_n_time(rules.FileStat(
        path=Path("/a/b/000_20101231_191530.jpg"),
        mtime=datetime(2010, 12, 31, 16, 15, 30))
        ) == (False, None)


def test_date_without_time(mocker: MockFixture) -> None:
    """Test rule 'date_without_time'."""
    mocker.patch("rules.PERIODS", PERIODS)
    mocker.patch("rules.SYSTEM_ZONE", SYSTEM_ZONE)

    assert rules.rule_date_without_time(rules.FileStat(
        path=Path("/a/b/20101231.jpg"),
        mtime=datetime(2010, 12, 31, 16, 15, 30))
        ) == (True, None)

    # The year before periods
    assert rules.rule_date_without_time(rules.FileStat(
        path=Path("/a/b/19990301.jpg"),
        mtime=datetime(2024, 12, 31, 1, 1, 0))
        ) == (True, None)

    # Incorrect mtime
    assert rules.rule_date_without_time(rules.FileStat(
        path=Path("/a/b/20101231.jpg"),
        mtime=datetime(2010, 11, 30, 16, 15, 30))
        ) == (True, datetime(2010, 12, 31, 16, 15, 30, tzinfo=SYSTEM_ZONE))

    # Filename date with dash
    assert rules.rule_date_without_time(rules.FileStat(
        path=Path("/a/b/2010-12-31.jpg"),
        mtime=datetime(2010, 12, 31, 16, 15, 30))
        ) == (True, None)


def test_date_in_dir(mocker: MockFixture) -> None:
    """Test rule 'date_in_dir'."""
    mocker.patch("rules.PERIODS", PERIODS)
    mocker.patch("rules.SYSTEM_ZONE", SYSTEM_ZONE)

    assert rules.rule_date_in_dir(rules.FileStat(
        path=Path("/a/b/2020-12-31/SNC00001.jpg"),
        mtime=datetime(2020, 12, 31, 16, 15, 30))
        ) == (True, None)

    # Directory with subdirectory
    assert rules.rule_date_in_dir(rules.FileStat(
        path=Path("/a/b/2020-12-31/abc/SNC00001.jpg"),
        mtime=datetime(2020, 12, 31, 16, 15, 30))
        ) == (True, None)

    # Directory name with extra symbols
    assert rules.rule_date_in_dir(rules.FileStat(
        path=Path("/a/b/2020-12-31 abc/SNC00001.jpg"),
        mtime=datetime(2020, 12, 31, 16, 15, 30))
        ) == (True, None)

    # Year only and it's correct
    assert rules.rule_date_in_dir(rules.FileStat(
        path=Path("/a/b/2020/SNC00001.jpg"),
        mtime=datetime(2020, 12, 31, 16, 15, 30))
        ) == (True, None)

    # Year only and it's wrong
    assert rules.rule_date_in_dir(rules.FileStat(
        path=Path("/a/b/2020/SNC00001.jpg"),
        mtime=datetime(2024, 12, 31, 16, 15, 30))
        ) == (True, datetime(2020, 12, 31, 16, 15, 30, tzinfo=SYSTEM_ZONE))
