"""
event_triggering.py

Beginner-friendly helpers for:
- running ObsPy coincidence_trigger on a (pre-trimmed) Stream
- extracting segmented "event" waveform windows
- plotting ON/OFF markers
- optionally writing MiniSEED
- building a pandas DataFrame "candidate event catalogue"

Designed to keep ObsPy calls visible and not overly abstract.

Typical use in a notebook:

    from event_triggering import run_trigger_wrapper_df

    st2 = stream_master.copy().trim(starttime=t0 + 400, endtime=t0 + 550)
    df = run_trigger_wrapper_df(st2, make_plots=False, write_mseed=False)
    df.head()

"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from obspy import Stream, UTCDateTime
from obspy.signal.trigger import coincidence_trigger


# ----------------------------
# Plotting helper
# ----------------------------

def plot_stream_with_on_off(st: Stream, on_time: UTCDateTime, off_time: UTCDateTime, show: bool = True):
    """
    Plot a Stream and draw ON/OFF vertical lines.
    """
    fig = st.plot(show=False, handle=True)
    ax = fig.axes[-1]

    ax.axvline(mdates.date2num(on_time), color="r", linestyle="--", lw=2)
    ax.axvline(mdates.date2num(off_time), color="g", linestyle="--", lw=2)

    ax.text(mdates.date2num(on_time), ax.get_ylim()[1], "ON", rotation=90, va="top")
    ax.text(mdates.date2num(off_time), ax.get_ylim()[1], "OFF", rotation=90, va="top")

    if show:
        plt.show()

    return fig


# ----------------------------
# Simple RMS + SNR helpers
# ----------------------------

def trace_rms(tr) -> float:
    """
    RMS of a single Trace. Returns NaN if empty.
    """
    x = np.asarray(tr.data, dtype=float)
    if x.size == 0:
        return float("nan")
    return float(np.sqrt(np.mean(x * x)))


def stream_median_rms(st: Stream) -> float:
    """
    Median RMS over traces in a Stream.
    Useful when a Stream has multiple channels and you want a robust summary.
    """
    vals = [trace_rms(tr) for tr in st]
    vals = [v for v in vals if np.isfinite(v)]
    return float(np.median(vals)) if vals else float("nan")

# ----------------------------
# DataFrame output (catalogue)
# ----------------------------

def extract_plot_write_events_to_dataframe(
    st: Stream,
    trig: Sequence[Dict[str, Any]],
    pretrigger_seconds: float = 10.0,
    posttrigger_seconds: float = 15.0,
    write_mseed: bool = False,
    outdir: str = ".",
    max_events: Optional[int] = None,
    make_plots: bool = True,
    filename_safe: bool = True,
    verbose: bool = False,
) -> pd.DataFrame:
    """
    Loop over coincidence_trigger results and return a DataFrame with one row per event segment.

    Columns include:
      - on_time / off_time (pandas datetimes)
      - duration_s
      - seed_ids (list)
      - output directory + filename + filepath
      - pre/post trigger seconds
      - coincidence_sum (if present)
      - RMS-based SNR estimate:
          snr_rms = median_rms(trigger_window) / median_rms(pretrigger_window)

    Optionally writes each segment to MiniSEED and plots it.
    """
    os.makedirs(outdir, exist_ok=True)

    rows: List[Dict[str, Any]] = []

    if not trig:
        print("No triggers found.")
        return pd.DataFrame(rows)

    for i, t in enumerate(trig):
        if (max_events is not None) and (i >= max_events):
            break

        on_time = t["time"]
        duration = float(t["duration"])
        off_time = on_time + duration

        # Event window (includes pre/post)
        st_event = st.copy().trim(
            starttime=on_time - pretrigger_seconds,
            endtime=off_time + posttrigger_seconds
        )

        # Signal-only window (trigger duration)
        st_signal = st.copy().trim(starttime=on_time, endtime=off_time)

        # Noise-only window (pretrigger portion)
        st_noise = st.copy().trim(
            starttime=on_time - pretrigger_seconds,
            endtime=on_time
        )

        # Simple RMS-based SNR
        signal_rms = stream_median_rms(st_signal)
        noise_rms = stream_median_rms(st_noise)
        if np.isfinite(signal_rms) and np.isfinite(noise_rms) and noise_rms > 0:
            snr_rms = float(signal_rms / noise_rms)
        else:
            snr_rms = float("nan")

        # Seed IDs present in extracted event
        seed_ids = sorted({tr.id for tr in st_event})

        # Output filename/path
        ts = on_time.isoformat()
        if filename_safe:
            ts = ts.replace(":", "")
        filename = f"{ts}.mseed"
        filepath = os.path.join(outdir, filename)

        # Optional plot
        if make_plots:
            plot_stream_with_on_off(st_event, on_time, off_time)

        # Optional write
        if write_mseed:
            st_event.write(filepath, format="MSEED")

        coincidence_sum = t.get("coincidence_sum", np.nan)

        if verbose:
            print(f"Event {i+1}/{len(trig)}  ON={on_time}  dur={duration:.2f}s  SNR~{snr_rms:.2f}")

        rows.append({
            "event_index": i,
            "on_time": on_time.datetime,
            "off_time": off_time.datetime,
            "duration_s": duration,
            "seed_ids": seed_ids,
            "n_seed_ids": len(seed_ids),
            "pretrigger_s": float(pretrigger_seconds),
            "posttrigger_s": float(posttrigger_seconds),
            "outdir": outdir,
            "filename": filename,
            "filepath": filepath,
            "wrote_file": bool(write_mseed),
            "coincidence_sum": coincidence_sum,
            "signal_rms": signal_rms,
            "noise_rms": noise_rms,
            "snr_rms": snr_rms,
        })

    return pd.DataFrame(rows)


# ----------------------------
# Wrapper: run trigger + return outputs
# ----------------------------

def run_trigger_wrapper_df(
    st: Stream,
    sta_seconds: float = 1.0,
    lta_seconds: float = 10.0,
    threshold_on: float = 2.5,
    threshold_off: float = 0.5,
    min_channels: int = 1,
    pretrigger_seconds: float = 10.0,
    posttrigger_seconds: float = 15.0,
    write_mseed: bool = False,
    outdir: str = ".",
    max_events: Optional[int] = None,
    make_plots: bool = True,
    filename_safe: bool = True,
) -> pd.DataFrame:
    """
    Run ObsPy coincidence_trigger on a pre-trimmed stream and return a DataFrame catalogue.

    Returns: pandas.DataFrame (one row per event segment)
    """
    print("Running coincidence trigger...")

    trig = coincidence_trigger(
        "recstalta",
        threshold_on,
        threshold_off,
        st,
        min_channels,
        sta=sta_seconds,
        lta=lta_seconds,
    )

    print(f"Starttime: {st[0].stats.starttime}")
    print(f"Endtime: {st[0].stats.endtime}")
    print(f"Number of triggers found: {len(trig)}")

    return extract_plot_write_events_to_dataframe(
        st,
        trig,
        pretrigger_seconds=pretrigger_seconds,
        posttrigger_seconds=posttrigger_seconds,
        write_mseed=write_mseed,
        outdir=outdir,
        max_events=max_events,
        make_plots=make_plots,
        filename_safe=filename_safe,
    )

def filter_events_df(
    df: pd.DataFrame,
    *,
    min_snr: Optional[float] = None,
    min_coincidence: Optional[float] = None,
    min_duration_s: Optional[float] = None,
    max_duration_s: Optional[float] = None,
) -> pd.DataFrame:
    """
    Return a filtered copy of the event catalogue DataFrame.
    """
    out = df.copy()

    if min_snr is not None and "snr_rms" in out.columns:
        out = out[out["snr_rms"] >= float(min_snr)]

    if min_coincidence is not None and "coincidence_sum" in out.columns:
        out = out[out["coincidence_sum"] >= float(min_coincidence)]

    if min_duration_s is not None and "duration_s" in out.columns:
        out = out[out["duration_s"] >= float(min_duration_s)]

    if max_duration_s is not None and "duration_s" in out.columns:
        out = out[out["duration_s"] <= float(max_duration_s)]

    return out.reset_index(drop=True)


def _safe_timestamp_for_filename(dt: pd.Timestamp) -> str:
    # ISO but remove characters that can be annoying in filenames
    # Example: 2009-03-20T12:34:56.789000 -> 2009-03-20T123456.789000
    s = dt.isoformat()
    s = s.replace(":", "")
    return s


def _event_day_dir(base_outdir: str, on_time: pd.Timestamp) -> str:
    # YYYY/MM/DD
    return os.path.join(
        base_outdir,
        f"{on_time.year:04d}",
        f"{on_time.month:02d}",
        f"{on_time.day:02d}",
    )


def save_event_plot_png(
    st_event: Stream,
    on_time: UTCDateTime,
    off_time: UTCDateTime,
    png_path: str,
):
    """
    Save a PNG plot for an event segment, with ON/OFF lines.
    """
    fig = plot_stream_with_on_off(st_event, on_time, off_time, False)
    fig.savefig(png_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

def export_events_from_catalogue(
    df: pd.DataFrame,
    *,
    base_outdir: str = "exported_events",
    write_mseed: bool = True,
    write_png: bool = True,
    # How to get waveforms:
    # Option A (simplest): you provide a Stream that covers the event windows
    st_continuous: Optional[Stream] = None,
    # Option B: df already has 'filepath' pointing to existing mseed segments
    use_existing_mseed_if_present: bool = True,
    max_events: Optional[int] = None,
) -> pd.DataFrame:
    """
    Export events from a catalogue DataFrame into YYYY/MM/DD directories.

    Files (MiniSEED and PNG) are mixed in the same day directory.

    Returns a copy of df with new columns:
      - export_dir, export_mseed_path, export_png_path
    """
    if "on_time" not in df.columns:
        raise ValueError("df must contain an 'on_time' column (datetime).")

    out = df.copy()
    out["export_dir"] = ""
    out["export_mseed_path"] = ""
    out["export_png_path"] = ""

    n = len(out)
    if max_events is not None:
        n = min(n, int(max_events))

    for i in range(n):
        row = out.iloc[i]
        on_dt = pd.to_datetime(row["on_time"])
        off_dt = pd.to_datetime(row["off_time"]) if "off_time" in out.columns else (on_dt + pd.to_timedelta(float(row["duration_s"]), unit="s"))

        export_dir = _event_day_dir(base_outdir, on_dt)
        os.makedirs(export_dir, exist_ok=True)

        stem = _safe_timestamp_for_filename(on_dt)

        mseed_path = os.path.join(export_dir, f"{stem}.mseed")
        png_path = os.path.join(export_dir, f"{stem}.png")

        # Build the event Stream (st_event)
        st_event: Optional[Stream] = None

        # If df already points to an existing mseed and we want to use it:
        if use_existing_mseed_if_present and "filepath" in out.columns:
            fp = row.get("filepath", "")
            if isinstance(fp, str) and fp and os.path.exists(fp):
                st_event = read(fp)

        # Otherwise, cut from continuous stream (requires st_continuous)
        if st_event is None:
            if st_continuous is None:
                raise ValueError(
                    "No waveform source available for export.\n"
                    "Either provide st_continuous=... that covers the event windows, "
                    "or ensure df['filepath'] points to existing MiniSEED files."
                )

            pre = float(row["pretrigger_s"]) if "pretrigger_s" in out.columns else 0.0
            post = float(row["posttrigger_s"]) if "posttrigger_s" in out.columns else 0.0

            on = UTCDateTime(on_dt.to_pydatetime())
            off = UTCDateTime(off_dt.to_pydatetime())

            st_event = st_continuous.copy().trim(
                starttime=on - pre,
                endtime=off + post
            )

        # Now write outputs
        if write_mseed:
            st_event.write(mseed_path, format="MSEED")

        if write_png:
            on = UTCDateTime(on_dt.to_pydatetime())
            off = UTCDateTime(off_dt.to_pydatetime())
            save_event_plot_png(st_event, on, off, png_path)

        out.at[out.index[i], "export_dir"] = export_dir
        out.at[out.index[i], "export_mseed_path"] = mseed_path if write_mseed else ""
        out.at[out.index[i], "export_png_path"] = png_path if write_png else ""

    return out



def plot_event_rate(
    df: pd.DataFrame,
    *,
    time_col: str = "on_time",
    bin_size: str = "1h",                 # pandas offset alias e.g. "10min", "30min", "1H", "1D"
    min_snr: Optional[float] = None,
    min_coincidence: Optional[float] = None,
    min_duration_s: Optional[float] = None,
    max_duration_s: Optional[float] = None,
    title: Optional[str] = None,
    show: bool = True,
    savepath: Optional[str] = None,
):
    """
    Plot event counts in fixed-width time bins over the whole catalogue.
    """
    if time_col not in df.columns:
        raise ValueError(f"df must contain '{time_col}' column.")

    dff = df.copy()
    dff[time_col] = pd.to_datetime(dff[time_col])
    dff = dff.sort_values(time_col)

    # Apply optional thresholds
    dff = filter_events_df(
        dff,
        min_snr=min_snr,
        min_coincidence=min_coincidence,
        min_duration_s=min_duration_s,
        max_duration_s=max_duration_s,
    )

    if len(dff) == 0:
        print("No events after filtering.")
        return None

    # Bin counts
    counts = (
        dff.set_index(time_col)
           .resample(bin_size)
           .size()
    )

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(counts.index, counts.values)

    ax.set_xlabel("Time")
    ax.set_ylabel(f"Events per {bin_size}")

    if title is None:
        title = "Event rate"
    ax.set_title(title)

    fig.autofmt_xdate()

    if savepath:
        fig.savefig(savepath, dpi=150, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close(fig)

    return fig

def plot_stream_with_event_markers(
    st: Stream,
    df: pd.DataFrame,
    *,
    on_col: str = "on_time",
    off_col: str = "off_time",
    show: bool = True,
    label_lines: bool = True,
    shade_events: bool = False,
    shade_alpha: float = 0.15,
    linewidth: float = 1.5,
    equal_scale: bool = False,
):
    """
    Plot a Stream and superimpose trigger ON/OFF times on ALL trace axes.

    Parameters
    ----------
    st : obspy.Stream
        Stream to plot.
    df : pandas.DataFrame
        Event catalogue containing at least `on_col` and `off_col`.
    on_col : str
        Column name for event start times.
    off_col : str
        Column name for event end times.
    show : bool
        If True, call plt.show().
    label_lines : bool
        Add legend labels (only on first axis to avoid duplicates).
    shade_events : bool
        If True, shade event windows.
    shade_alpha : float
        Transparency for shading.
    linewidth : float
        Line width for markers.
    equal_scale : bool
        Passed to st.plot(). Default False (recommended for multi-trace plots).

    Returns
    -------
    fig, axes
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")

    if on_col not in df.columns or off_col not in df.columns:
        raise ValueError(f"df must contain '{on_col}' and '{off_col}'.")

    if len(st) == 0:
        raise ValueError("Stream is empty.")

    # Clean + convert times
    dff = df[[on_col, off_col]].copy()
    dff[on_col] = pd.to_datetime(dff[on_col], errors="coerce")
    dff[off_col] = pd.to_datetime(dff[off_col], errors="coerce")
    dff = dff.dropna(subset=[on_col, off_col]).sort_values(on_col)

    # Plot stream (important change: equal_scale=False default)
    fig = st.plot(show=False, handle=True, equal_scale=equal_scale)
    axes = fig.axes

    if len(dff) == 0:
        if show:
            plt.show()
        return fig, axes

    # Convert times once
    on_nums = mdates.date2num(dff[on_col].dt.to_pydatetime())
    off_nums = mdates.date2num(dff[off_col].dt.to_pydatetime())

    # Loop over ALL axes (one per Trace)
    for i, ax in enumerate(axes):
        ymin, ymax = ax.get_ylim()

        # Add ON/OFF lines
        if label_lines and i == 0:
            ax.vlines(on_nums, ymin, ymax, color="r", lw=linewidth, label="Trigger On")
            ax.vlines(off_nums, ymin, ymax, color="b", lw=linewidth, label="Trigger Off")
            ax.legend()
        else:
            ax.vlines(on_nums, ymin, ymax, color="r", lw=linewidth)
            ax.vlines(off_nums, ymin, ymax, color="b", lw=linewidth)

        # Optional shading
        if shade_events:
            for on_num, off_num in zip(on_nums, off_nums):
                ax.axvspan(on_num, off_num, alpha=shade_alpha)

    fig.canvas.draw()

    if show:
        plt.show()

    return fig, axes