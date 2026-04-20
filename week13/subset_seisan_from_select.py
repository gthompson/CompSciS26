#!/usr/bin/env python3
"""
subset_select_out.py

Split a SEISAN SELECT output catalog (select.out) into individual S-files
and copy referenced waveform files into a new SEISAN-style subset database.

Example
-------
python subset_select_out.py \
    --select-out /home/glenn/select.out \
    --dest-root /home/glenn/mydata/seisan \
    --dbname MVVT \
    --mainclass L

Notes
-----
- Destination S-files are written to:
      REA/{DBNAME}/YYYY/MM/
- Referenced waveform files are copied to:
      WAV/{DBNAME}/YYYY/MM/
- DBNAME is padded to 5 characters with underscores for filesystem layout.



Example usage

python subset_select_out.py \
    --select-out ~/select.out \
    --dest-root ~/mydata/seisan \
    --dbname MVVT \
    --mainclass L \
    --verbose

This will create:

~/mydata/seisan/
├── REA/
│   └── MVVT_/
│       └── YYYY/MM/*.SYYYYMM
└── WAV/
    └── MVVT_/
        └── YYYY/MM/*


A few practical notes

The main SEISAN manual point to remember is that the S-file is the basic per-event unit, and it already contains the waveform filenames needed to reconstruct an event subset. That is why this workflow is so natural.  ￼

Also, if you only wanted waveform extraction without writing your own Python, SEISAN’s GET WAV can take select.out directly and produce copy commands for the referenced waveform files. Your Python version is still preferable here because it gives you a reusable FLOVOpy-native subsetting workflow.  ￼

One caution: in this script I defaulted mainclass="L" for the output S-file naming, because these are local volcanic events. If your selected catalog includes other top-level event classes, you may want to make that smarter and parse the original class letter from the event header or ID line before naming the output S-file.

Another possible improvement is to rewrite waveform references inside each copied S-file so they point explicitly to the new subset location. In many cases that is not necessary, because SEISAN can find waveform files by name in the active database layout, but it can be useful if you want the subset to be completely portable.

The one structural point I am slightly unsure about is whether your select.out is perfectly blank-line delimited throughout; most SEISAN Nordic multi-event outputs are, so this splitter should work, but if your catalog has any odd formatting, the split step may need to be made a bit more defensive.

"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path
from typing import List

from obspy.io.nordic.core import readheader

from flovopy.seisanio.core.sfile import Sfile
from flovopy.seisanio.utils.helpers import filetime2spath


def pad_dbname(dbname: str) -> str:
    dbname = dbname.strip()
    if not dbname:
        raise ValueError("Database name cannot be empty")
    if len(dbname) > 5:
        raise ValueError("SEISAN database names must be at most 5 characters")
    return dbname + "_" * (5 - len(dbname))


def split_nordic_catalog(text: str) -> List[str]:
    """
    Split a Nordic multi-event catalog into individual event blocks.

    Assumes events are separated by one or more blank lines.
    """
    events: List[str] = []
    current: List[str] = []

    for line in text.splitlines(keepends=True):
        if line.strip() == "":
            if current:
                events.append("".join(current))
                current = []
        else:
            if not line.endswith("\n"):
                line += "\n"
            current.append(line)

    if current:
        events.append("".join(current))

    return events


def get_event_time(event_text: str):
    """
    Read event origin/header time by writing to a temporary file and using
    ObsPy's Nordic header reader.
    """
    with tempfile.NamedTemporaryFile("w", suffix=".nor", delete=False) as tf:
        tf.write(event_text)
        tmp_path = tf.name

    try:
        ev = readheader(tmp_path)
        if not ev.origins:
            raise ValueError("No origin found in event header")
        return ev.origins[0].time
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def write_event_block(dest_sfile: Path, event_text: str, overwrite: bool = False) -> None:
    dest_sfile.parent.mkdir(parents=True, exist_ok=True)
    if dest_sfile.exists() and not overwrite:
        return
    dest_sfile.write_text(event_text)


def copy_referenced_wavs(
    sfile_path: Path,
    dest_root: Path,
    dbname_fs: str,
    overwrite: bool = False,
) -> list[str]:
    """
    Use the attached Sfile class to discover referenced waveform files, then copy
    them into WAV/{dbname}/YYYY/MM under the destination archive root.
    """
    copied = []
    sf = Sfile(str(sfile_path))

    for wavobj in sf.wavfileobjs:
        src = Path(wavobj.path)

        if not src.exists():
            copied.append(f"MISSING: {src}")
            continue

        # Build destination WAV directory from the event time
        filetime = sf.filetime
        if filetime is None:
            copied.append(f"NO_FILETIME_FOR: {src}")
            continue

        dest_dir = dest_root / "WAV" / dbname_fs / f"{filetime.year:04d}" / f"{filetime.month:02d}"
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest = dest_dir / src.name
        if dest.exists() and not overwrite:
            copied.append(f"EXISTS: {dest}")
            continue

        shutil.copy2(src, dest)
        copied.append(f"COPIED: {src} -> {dest}")

    return copied


def process_select_out(
    select_out: Path,
    dest_root: Path,
    dbname: str,
    mainclass: str = "L",
    overwrite: bool = False,
    verbose: bool = False,
) -> None:
    dbname_fs = pad_dbname(dbname)

    text = select_out.read_text()
    events = split_nordic_catalog(text)

    print(f"Found {len(events)} event blocks in {select_out}")

    log_lines: list[str] = []

    for i, event_text in enumerate(events, start=1):
        try:
            event_time = get_event_time(event_text)

            dest_sfile = Path(
                filetime2spath(
                    event_time,
                    mainclass=mainclass,
                    db=dbname_fs,
                    seisan_top=str(dest_root),
                    fullpath=True,
                )
            )

            write_event_block(dest_sfile, event_text, overwrite=overwrite)

            wav_logs = copy_referenced_wavs(
                dest_sfile,
                dest_root=dest_root,
                dbname_fs=dbname_fs,
                overwrite=overwrite,
            )

            log_lines.append(f"\nEVENT {i}: {dest_sfile}")
            log_lines.extend(wav_logs)

            if verbose and i % 100 == 0:
                print(f"Processed {i}/{len(events)} events")

        except Exception as e:
            msg = f"ERROR event {i}: {e}"
            log_lines.append(msg)
            print(msg)

    logfile = dest_root / f"subset_{dbname_fs}_copy.log"
    logfile.write_text("\n".join(log_lines))
    print(f"Done. Log written to {logfile}")


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Split select.out into S-files and copy referenced waveform files"
    )
    p.add_argument("--select-out", required=True, type=Path, help="Path to select.out")
    p.add_argument("--dest-root", required=True, type=Path, help="Destination SEISAN root")
    p.add_argument("--dbname", required=True, help="New subset database name (<=5 chars)")
    p.add_argument(
        "--mainclass",
        default="L",
        help="SEISAN main event class letter to use in output S-file names (default: L)",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing S-files/WAV files in destination",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Print progress",
    )
    return p


def main() -> None:
    args = build_argparser().parse_args()

    process_select_out(
        select_out=args.select_out,
        dest_root=args.dest_root,
        dbname=args.dbname,
        mainclass=args.mainclass,
        overwrite=args.overwrite,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()


