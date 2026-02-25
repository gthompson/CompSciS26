import os
import numpy as np
from obspy import Stream, UTCDateTime

def _normalize_trace(tr, verbose=True):
    """
    Normalize trace so merge works:
    - Convert masked arrays → ndarray
    - Force float32 dtype (BEFORE and AFTER resample)
    - Round sampling rate to nearest integer
    """
    tr = tr.copy()

    # Masked array → ndarray
    if isinstance(tr.data, np.ma.MaskedArray):
        tr.data = tr.data.filled(np.nan)

    # Force float32 early (some operations behave better)
    if tr.data.dtype != np.float32:
        tr.data = tr.data.astype(np.float32, copy=False)

    # Round sampling rate
    sr_old = float(tr.stats.sampling_rate)
    sr_new = float(round(sr_old))

    if abs(sr_old - sr_new) > 1e-6:
        if verbose:
            print(f"[SR] {tr.id}: {sr_old} -> {sr_new} Hz (resample)")
        tr.resample(sr_new)

        # IMPORTANT: resample often promotes dtype to float64 → force back to float32
        if tr.data.dtype != np.float32:
            tr.data = tr.data.astype(np.float32, copy=False)

    # Final safety: if anything weird slipped in, force float32
    if tr.data.dtype != np.float32:
        tr.data = np.asarray(tr.data, dtype=np.float32)

    return tr


def _pad_to_full_day(tr, day_start, day_end):
    """
    Pad trace with NaNs so it spans full day.
    """
    tr = tr.copy()
    tr.trim(day_start, day_end, pad=True, fill_value=np.nan)
    return tr


def write_stream_to_sds(
    st,
    sds_root,
    data_type="D",
    loc_blank_as="",
    merge=True,
    verbose=True,
):
    """
    SMART VERSION — API compatible with naive version.

    Writes exactly ONE MiniSEED file per channel per day,
    padding gaps with NaNs and normalizing traces so merge succeeds.
    """

    st = st.copy()

    # Normalize traces
    st_norm = Stream()
    for tr in st:
        try:
            st_norm += _normalize_trace(tr, verbose=verbose)
        except Exception as e:
            print(f"⚠️ Normalize failed for {tr.id}: {e}")

    st = st_norm

    # Determine unique day boundaries
    days = sorted({tr.stats.starttime.date for tr in st})

    for day_date in days:

        day_start = UTCDateTime(day_date)
        day_end = day_start + 86400

        # Select traces overlapping this day
        st_day = st.copy().trim(day_start, day_end)

        # Group by NET.STA.LOC.CHA
        ids = sorted({tr.id for tr in st_day})

        for tid in ids:

            st_id = st_day.select(id=tid)

            if len(st_id) == 0:
                continue

            # Merge safely
            if merge:
                try:
                    st_id.merge(method=1, fill_value=np.nan)
                except Exception as e:
                    print(f"⚠️ Merge failed for {tid}: {e}")

            tr = st_id[0]

            # Pad to full day
            tr = _pad_to_full_day(tr, day_start, day_end)

            net = tr.stats.network
            sta = tr.stats.station
            loc = (tr.stats.location or "").strip()
            cha = tr.stats.channel

            if loc == "":
                loc = loc_blank_as

            year = day_start.year
            jjj = f"{day_start.julday:03d}"

            # SDS directory
            sds_dir = os.path.join(
                sds_root,
                f"{year}",
                net,
                sta,
                f"{cha}.{data_type}"
            )
            os.makedirs(sds_dir, exist_ok=True)

            fname = f"{net}.{sta}.{loc}.{cha}.{data_type}.{year}.{jjj}"
            full_path = os.path.join(sds_dir, fname)

            if verbose:
                print(f"Writing {full_path}")

            tr.write(full_path, format="MSEED")