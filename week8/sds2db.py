#!/usr/bin/env python3
"""
Traverse an SDS archive, select files using wildcards, and ingest into an Antelope DB
via miniseed2db.

SDS layout expected:
  SDS_ROOT/YEAR/NET/STA/CHAN.TYPE/NET.STA.LOC.CHAN.TYPE.YEAR.JJJ

Example filename:
  AV.RDT..EHZ.D.2009.079
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import subprocess
from pathlib import Path
from typing import Iterable, Iterator, Optional, Tuple


def parse_sds_filename(fname: str) -> Optional[Tuple[str, str, str, str, str, str, str]]:
    """
    Parse an SDS filename into components:
      NET, STA, LOC, CHA, TYPE, YEAR, JJJ

    Returns None if it doesn't look like an SDS filename.
    """
    parts = fname.split(".")
    # NET.STA.LOC.CHA.TYPE.YEAR.JJJ  -> 7 parts
    if len(parts) != 7:
        return None
    net, sta, loc, cha, dtype, year, jjj = parts
    return net, sta, loc, cha, dtype, year, jjj


def iter_sds_files(
    sds_root: Path,
    net: str = "*",
    sta: str = "*",
    loc: str = "*",
    cha: str = "*",
    dtype: str = "D",
    year: str = "*",
    jday: str = "*",
) -> Iterator[Path]:
    """
    Yield SDS files matching wildcard patterns.
    """
    # We intentionally traverse by YEAR/NET/STA to keep it fast.
    # The deeper "CHAN.TYPE" dir is derived from channel code + dtype.
    root = sds_root

    # If year is concrete (e.g., "2009"), restrict; else glob all years.
    year_dirs = [root / year] if year != "*" else [p for p in root.iterdir() if p.is_dir()]

    for ydir in year_dirs:
        if not ydir.exists():
            continue

        for netdir in ydir.glob("*"):
            if not netdir.is_dir() or not fnmatch.fnmatch(netdir.name, net):
                continue

            for stadir in netdir.glob("*"):
                if not stadir.is_dir() or not fnmatch.fnmatch(stadir.name, sta):
                    continue

                # Inside STA: e.g. EHZ.D, BHZ.D, etc.
                for chantypedir in stadir.glob("*.?*"):  # loosely match "EHZ.D" etc.
                    if not chantypedir.is_dir():
                        continue

                    # Expect "CHAN.TYPE" directory
                    if "." not in chantypedir.name:
                        continue
                    chan_dir, type_dir = chantypedir.name.split(".", 1)

                    if not fnmatch.fnmatch(chan_dir, cha):
                        continue
                    if dtype and type_dir != dtype:
                        continue

                    # Now match filenames inside
                    for f in chantypedir.iterdir():
                        if not f.is_file():
                            continue
                        parsed = parse_sds_filename(f.name)
                        if parsed is None:
                            continue
                        fnet, fsta, floc, fcha, fdtype, fyear, fjday = parsed

                        # Wildcard checks against filename fields
                        if not fnmatch.fnmatch(fnet, net):
                            continue
                        if not fnmatch.fnmatch(fsta, sta):
                            continue
                        if not fnmatch.fnmatch(floc, loc):
                            continue
                        if not fnmatch.fnmatch(fcha, cha):
                            continue
                        if dtype and fdtype != dtype:
                            continue
                        if not fnmatch.fnmatch(fyear, year):
                            continue
                        if not fnmatch.fnmatch(fjday, jday):
                            continue

                        yield f


def run_miniseed2db(files: Iterable[Path], dbname: str, dry_run: bool, batch_size: int) -> None:
    """
    Run miniseed2db on discovered files.
    - If batch_size > 1, call miniseed2db with multiple files per invocation (faster).
    """
    files = list(files)
    if not files:
        print("No matching SDS files found.")
        return

    print(f"Found {len(files)} SDS files to ingest into DB: {dbname}")

    # Batch calls to reduce process overhead.
    batch: list[str] = []
    for f in files:
        batch.append(str(f))
        if len(batch) >= batch_size:
            cmd = ["miniseed2db", *batch, dbname]
            if dry_run:
                print("DRY RUN:", " ".join(cmd))
            else:
                subprocess.run(cmd, check=True)
            batch = []

    if batch:
        cmd = ["miniseed2db", *batch, dbname]
        if dry_run:
            print("DRY RUN:", " ".join(cmd))
        else:
            subprocess.run(cmd, check=True)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Traverse SDS archive with wildcards and ingest matching MiniSEED to Antelope DB using miniseed2db."
    )
    ap.add_argument("sds_root", type=str, help="Root of SDS archive")
    ap.add_argument("dbname", type=str, help="Antelope database name (output prefix)")

    ap.add_argument("--net", default="*", help="Network wildcard (e.g., AV)")
    ap.add_argument("--sta", default="*", help="Station wildcard (e.g., RDT or RD*)")
    ap.add_argument("--loc", default="*", help="Location wildcard (e.g., '' is stored as blank in filename; use '*' usually)")
    ap.add_argument("--cha", default="*", help="Channel wildcard (e.g., EHZ or BH*)")
    ap.add_argument("--type", default="D", help="SDS data type (usually D)")

    ap.add_argument("--year", default="*", help="Year wildcard (e.g., 2009)")
    ap.add_argument("--jday", default="*", help="Julian day wildcard (e.g., 079 or 07*)")

    ap.add_argument("--dry-run", action="store_true", help="Print what would run, but do not execute miniseed2db")
    ap.add_argument("--batch-size", type=int, default=25, help="How many files per miniseed2db call (speed).")

    args = ap.parse_args()

    sds_root = Path(args.sds_root).expanduser().resolve()

    files = iter_sds_files(
        sds_root=sds_root,
        net=args.net,
        sta=args.sta,
        loc=args.loc,
        cha=args.cha,
        dtype=args.type,
        year=args.year,
        jday=args.jday,
    )

    run_miniseed2db(files, dbname=args.dbname, dry_run=args.dry_run, batch_size=max(1, args.batch_size))


if __name__ == "__main__":
    main()