"""
sds_antelope.py

Traverse an SDS archive, select files using wildcards, and ingest into an Antelope DB
via `miniseed2db`.

SDS layout expected:
  SDS_ROOT/YEAR/NET/STA/CHAN.TYPE/NET.STA.LOC.CHAN.TYPE.YEAR.JJJ

Example filename:
  AV.RDT..EHZ.D.2009.079
"""
from __future__ import annotations

import fnmatch
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Optional, Sequence, Tuple

SDSParts = Tuple[str, str, str, str, str, str, str]
#            NET  STA  LOC  CHA  TYPE YEAR JJJ


@dataclass(frozen=True)
class SDSQuery:
    net: str = "*"
    sta: str = "*"
    loc: str = "*"
    cha: str = "*"
    dtype: str = "D"
    year: str = "*"
    jday: str = "*"


def parse_sds_filename(fname: str) -> Optional[SDSParts]:
    parts = fname.split(".")
    if len(parts) != 7:
        return None
    net, sta, loc, cha, dtype, year, jjj = parts
    if not (net and sta and cha and dtype and year and jjj):
        return None
    return net, sta, loc, cha, dtype, year, jjj


def _iter_year_dirs(root: Path, year_pat: str) -> Iterator[Path]:
    if year_pat != "*":
        y = root / year_pat
        if y.is_dir():
            yield y
        return
    for p in root.iterdir():
        if p.is_dir():
            yield p


def _day_window_from_year_jday(year: str, jday: str):
    """
    Return (day_start, day_end) as ObsPy UTCDateTime for YEAR/JJJ.
    day_end is exclusive (start + 86400s).
    """
    try:
        y = int(year)
        j = int(jday)
    except ValueError:
        return None

    # Local import: only required if date filtering is used.
    from obspy import UTCDateTime  # type: ignore

    day_start = UTCDateTime(year=y, julday=j)  # midnight at start of that Julian day
    day_end = day_start + 86400
    return day_start, day_end


def _overlaps_interval(day_start, day_end, starttime, endtime) -> bool:
    """
    True if [day_start, day_end) overlaps [starttime, endtime] (inclusive end).
    - If starttime is None => unbounded on left
    - If endtime is None => unbounded on right
    """
    if starttime is None and endtime is None:
        return True
    if starttime is None:
        # overlaps if day_start <= endtime
        return day_start <= endtime
    if endtime is None:
        # overlaps if day_end > starttime
        return day_end > starttime

    # Treat endtime as inclusive by nudging comparisons appropriately:
    # Overlap of [a,b) with [c,d] is: (b > c) and (a <= d)
    return (day_end > starttime) and (day_start <= endtime)


def iter_sds_files(
    sds_root: Path,
    query: SDSQuery = SDSQuery(),
    *,
    starttime=None,  # ObsPy UTCDateTime
    endtime=None,    # ObsPy UTCDateTime
) -> Iterator[Path]:
    """
    Yield SDS files matching wildcard patterns in `query`, optionally restricted
    to those whose day-file interval overlaps [starttime, endtime].

    Notes:
    - SDS daily files represent one day: [00:00, 24:00) UTC for YEAR/JJJ.
    - If you specify start/end times within a day, the whole day-file is included
      if it overlaps your interval.
    """
    root = Path(sds_root).expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"SDS root not found or not a directory: {root}")

    # If date filtering is requested, validate the types a bit (duck-typing).
    if starttime is not None and not hasattr(starttime, "timestamp"):
        raise TypeError("starttime must be an ObsPy UTCDateTime (or compatible), or None")
    if endtime is not None and not hasattr(endtime, "timestamp"):
        raise TypeError("endtime must be an ObsPy UTCDateTime (or compatible), or None")

    for ydir in _iter_year_dirs(root, query.year):
        for netdir in ydir.iterdir():
            if not netdir.is_dir() or not fnmatch.fnmatch(netdir.name, query.net):
                continue

            for stadir in netdir.iterdir():
                if not stadir.is_dir() or not fnmatch.fnmatch(stadir.name, query.sta):
                    continue

                for chantypedir in stadir.iterdir():
                    if not chantypedir.is_dir():
                        continue
                    if "." not in chantypedir.name:
                        continue

                    chan_dir, type_dir = chantypedir.name.split(".", 1)
                    if not fnmatch.fnmatch(chan_dir, query.cha):
                        continue
                    if query.dtype and type_dir != query.dtype:
                        continue

                    for f in chantypedir.iterdir():
                        if not f.is_file():
                            continue

                        parsed = parse_sds_filename(f.name)
                        if parsed is None:
                            continue

                        fnet, fsta, floc, fcha, fdtype, fyear, fjday = parsed

                        if not fnmatch.fnmatch(fnet, query.net):
                            continue
                        if not fnmatch.fnmatch(fsta, query.sta):
                            continue
                        if not fnmatch.fnmatch(floc, query.loc):
                            continue
                        if not fnmatch.fnmatch(fcha, query.cha):
                            continue
                        if query.dtype and fdtype != query.dtype:
                            continue
                        if not fnmatch.fnmatch(fyear, query.year):
                            continue
                        if not fnmatch.fnmatch(fjday, query.jday):
                            continue

                        # Date range filter (day-file overlap)
                        if starttime is not None or endtime is not None:
                            day_win = _day_window_from_year_jday(fyear, fjday)
                            if day_win is None:
                                continue
                            day_start, day_end = day_win
                            if not _overlaps_interval(day_start, day_end, starttime, endtime):
                                continue

                        yield f


def chunked(iterable: Iterable[Path], n: int) -> Iterator[list[Path]]:
    if n < 1:
        raise ValueError("chunk size n must be >= 1")
    batch: list[Path] = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= n:
            yield batch
            batch = []
    if batch:
        yield batch


import os
import shutil
import subprocess


def source_antelope_env(setup_script="/opt/antelope/5.15/setup.sh"):
    """
    Source the Antelope setup.sh and import its environment variables
    into the current Python process.
    """
    command = f"bash -c 'source {setup_script} && env'"
    proc = subprocess.run(command, shell=True, capture_output=True, text=True)

    if proc.returncode != 0:
        raise RuntimeError(f"Failed to source {setup_script}")

    for line in proc.stdout.splitlines():
        key, _, value = line.partition("=")
        os.environ[key] = value


def ensure_miniseed2db_on_path():
    if shutil.which("miniseed2db") is None:
        source_antelope_env()

    if shutil.which("miniseed2db") is None:
        raise RuntimeError(
            "miniseed2db not found even after sourcing Antelope environment."
        )


def run_miniseed2db(
    files: Iterable[Path],
    dbname: str,
    *,
    dry_run: bool = True,
    batch_size: int = 25,
    check: bool = True,
    extra_args: Optional[Sequence[str]] = None,
    sort: bool = True,
) -> int:
    ensure_miniseed2db_on_path()
    extra_args = list(extra_args) if extra_args else []

    if sort:
        file_list = sorted([Path(f) for f in files])
        files_iter: Iterable[Path] = file_list
    else:
        files_iter = files

    processed = 0
    for batch in chunked(files_iter, batch_size):
        cmd = ["miniseed2db", *extra_args, *[str(p) for p in batch], dbname]
        processed += len(batch)
        if dry_run:
            print("DRY RUN:", " ".join(cmd))
        else:
            subprocess.run(cmd, check=check, cwd="/")

    if processed == 0:
        print("No matching SDS files found.")
    else:
        print(f"Processed {processed} files into DB: {dbname}")

    return processed