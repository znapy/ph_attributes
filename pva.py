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
from typing import Iterable

from helpers import to_unixtime
import rules

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
        print("The changed files:")
    if not args.change_files:
        print("The files will not be changed"
              " (execute with flag '-c' if need to change them):")
    return args

def _apply_new_date(new_date: datetime, file_stat: rules.FileStat,
                    args: argparse.Namespace) -> None:
    """Apply new date."""
    message = f"{file_stat.path} {file_stat.mtime: %Y-%m-%d_%H:%M:%S}" \
              f" -> {new_date: %Y-%m-%d_%H:%M:%S}"

    if args.change_files:
        unix_time = to_unixtime(new_date)
        os.utime(file_stat.path, times=(unix_time, unix_time))

    print(message)

def apply_rules(file_stat: rules.FileStat, args: argparse.Namespace) -> bool:
    """Apply rules."""
    all_rules: Iterable[rules.Rule] = (  # For type checker
        rules.rule_date_n_time,
        rules.rule_date_n_time_prefix,
    )

    for rule in all_rules:
        appropriate, new_date = rules.appropriate(rule, file_stat)
        if new_date is not None:
            _apply_new_date(new_date, file_stat, args)
        if appropriate:
            # only first appropriate rule is needed
            return new_date is not None
    return False

def main() -> None:
    """Main function."""
    args = get_args()

    applies = False
    for source_dir in {period.path for period in rules.PERIODS}:
        for dirpath, _, files in source_dir.walk(on_error=print):
            for filename in files:
                file_stat = rules.FileStat(Path(dirpath) / filename)
                applies = apply_rules(file_stat, args) | applies
    if not applies:
        print("No files appropriate for the rules.")


if __name__ == "__main__":
    main()
