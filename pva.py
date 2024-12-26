#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo and video attributes - change in files the time of last modification.

Rules:
- periods with time-zones
- file name patterns to get dates from it
- paths to folders with date patterns in name

homepage: https://github.com/znapy/pv-attributes
Copyright 2024 Alic Znapy
SPDX-License-Identifier: Apache-2.0
"""

import argparse
from datetime import datetime
import os
from pathlib import Path
import sys
from typing import Iterable

from helpers import to_datetime
from rules import SYSTEM_ZONE, PERIODS, Rule, FileStat, rule_date_n_time
# os.utime(p, times=(st.st_atime, st.st_mtime))

def get_args() -> argparse.Namespace:
    """Parse launch parameters."""
    parser = argparse.ArgumentParser(
        description=f"{__doc__}",
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        '-c', '--change-files', action='store_true',
        help='Change the time of last modification in files.'
             ' Without this option, the script will only'
             ' display the changes that will be made.')

    args = parser.parse_args()
    if args.change_files:
        print("Change files.")
    else:
        print("Only display changes.")
    return args

def get_file_stat(path: Path) -> FileStat:
    """Get file stat."""
    return FileStat(path=path,
                    mtime=to_datetime(path.stat().st_mtime, SYSTEM_ZONE))


def rules() -> Iterable[Rule]:
    """Get rules."""
    return (
        rule_date_n_time,
    )

def apply_rule(func: Rule, file_stat: FileStat
               ) -> tuple[bool, datetime | None]:
    """
    Try to apply the rule to FileStat.

    return is it applied and different datetime needed
    """
    return func(file_stat)


def main() -> None:
    """Main function."""
    args = get_args()

    checked_paths = []
    for period in PERIODS:
        if period.path in checked_paths:
            continue
        checked_paths.append(period.path)
        for dirpath, _, files in period.path.walk(on_error=print):
            for filename in files:
                file_stat = get_file_stat(Path(dirpath) / filename)
                for rule in rules():
                    applied, new_dt = apply_rule(rule, file_stat)
                    if new_dt:
                        print(f"{file_stat.path} {file_stat.mtime} -> {new_dt}")
                    if applied:
                        break

if __name__ == "__main__":
    main()
