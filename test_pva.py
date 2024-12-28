"""Pytests for the pva module."""

from datetime import datetime
from pathlib import Path
from pytest_mock import MockFixture
import tempfile
from zoneinfo import ZoneInfo

from config_example import Period, SYSTEM_ZONE
import pva


def _configure_tmp_dir(path: Path) -> tuple[list[Period], Path]:
    subdir = path / "name with spaces"
    subdir.mkdir()
    filepath = subdir / '20231231_191530.jpg'
    with open(filepath, 'w') as f:
        f.write('')

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

def test_main(mocker: MockFixture) -> None:
    """Test main function - scenario for 1 file."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        periods, filepath = _configure_tmp_dir(Path(tmp_dir))
        unix_time = 1704050130  # date from filename in *filepath*

        mocker.patch("pva.rules.PERIODS", periods)
        mocker.patch("pva.rules.SYSTEM_ZONE", SYSTEM_ZONE)
        mocker.patch("pva.get_args",
                     lambda: mocker.MagicMock(change_files=True))

        assert int(filepath.stat().st_mtime) != unix_time
        pva.main()
        assert int(filepath.stat().st_mtime) == unix_time
