#!/usr/bin/env python3
"""Source-verified audit of T17 MLFF-MD production trajectories.

The raw production files live under computational_v2/mlff/v3/t17.  This script
deduplicates repeated checkpoint rows, drops per-segment equilibration, and
reports the Al-anion standoff metrics used in the interface-composition story.
"""
from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "computational_v2" / "mlff" / "v3" / "t17"
OUT = ROOT / "results" / "T17_reactive"

RUNS = {
    "bare_neutral_matched_500ps": {
        "files": ["bare_final_s1_cv.csv", "bare_final_cv.csv"],
        "teq_ps": 50.0,
        "role": "primary neutral matched",
    },
    "poly_neutral_matched_500ps": {
        "files": ["poly_r6_s1_cv.csv", "poly_r6_cv.csv"],
        "teq_ps": 50.0,
        "role": "primary neutral matched",
    },
    "bare_qcond_100ps": {
        "files": ["bare_qcond_cv.csv"],
        "teq_ps": 50.0,
        "role": "charge-conditioned q run",
    },
    "poly_qcond_100ps": {
        "files": ["poly_qcond_cv.csv"],
        "teq_ps": 50.0,
        "role": "charge-conditioned q run",
    },
    "poly_qm2_1ns": {
        "files": ["poly_qm2_1ns_cv.csv"],
        "teq_ps": 50.0,
        "role": "poly q=-2 long negative control",
    },
    "bare_qm1_unstable": {
        "files": ["bare_qm1_cv.csv"],
        "teq_ps": 5.0,
        "role": "excluded unstable charged run",
    },
}


def ffloat(value: str) -> float:
    try:
        return float(value)
    except Exception:
        return math.nan


def read_rows(name: str) -> list[dict[str, float | str]]:
    path = RAW / name
    rows: list[dict[str, float | str]] = []
    seen: set[int] = set()
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            step = int(float(row["step"]))
            if step in seen:
                continue
            seen.add(step)
            parsed: dict[str, float | str] = {"file": name, "step": step}
            for key, value in row.items():
                if key == "step":
                    continue
                parsed[key] = ffloat(value)
            rows.append(parsed)
    return rows


def log_status(log_name: str) -> dict[str, int | str | None]:
    path = RAW / log_name
    if not path.exists():
        return {"log": log_name, "exists": 0, "cap": None, "nan": None, "done": 0}
    text = path.read_text(errors="ignore").splitlines()
    cap = nan = None
    done = 0
    for line in text:
        if "DONE" in line:
            done = 1
        match = re.search(r"cap=(\d+)\s+nan=(\d+)", line)
        if match:
            cap = int(match.group(1))
            nan = int(match.group(2))
    return {"log": log_name, "exists": 1, "cap": cap, "nan": nan, "done": done}


def summarize(label: str, spec: dict[str, object]) -> dict[str, object]:
    teq = float(spec["teq_ps"])
    all_rows: list[dict[str, float | str]] = []
    segments = []
    for name in spec["files"]:  # type: ignore[index]
        rows = read_rows(str(name))
        prod = [
            row
            for row in rows
            if float(row["t_ps"]) > teq
            and math.isfinite(float(row["Epot_eV"]))
            and float(row["T_K"]) < 1000.0
        ]
        segments.append(
            {
                "file": name,
                "rows_dedup": len(rows),
                "tmax_ps": max(float(row["t_ps"]) for row in rows),
                "prod_rows_after_teq": len(prod),
            }
        )
        all_rows.extend(prod)

    out: dict[str, object] = {
        "label": label,
        "role": spec["role"],
        "files": spec["files"],
        "teq_ps_per_segment": teq,
        "segments": segments,
        "n_prod_rows": len(all_rows),
        "production_valid": bool(all_rows),
    }
    for name in spec["files"]:  # type: ignore[index]
        out[f"log_{Path(str(name)).stem}"] = log_status(Path(str(name)).stem.replace("_cv", "") + ".log")

    if not all_rows:
        out["exclusion_reason"] = "no finite, T<1000 K production rows after equilibration cut"
        return out

    slab = np.array([float(row["Al_slabMin_A"]) for row in all_rows], dtype=float)
    height = np.array([float(row["Al_height_A"]) for row in all_rows], dtype=float)
    ncl = np.array([float(row["Al_nCl"]) for row in all_rows], dtype=float)
    si = np.array([float(row["Al_SiMin_A"]) for row in all_rows], dtype=float)
    times = np.array([float(row["t_ps"]) for row in all_rows], dtype=float)

    out.update(
        {
            "sampling_dt_ps": float(np.nanmedian(np.diff(np.unique(times)))) if len(times) > 2 else math.nan,
            "Al_slabMin_mean_A": float(np.nanmean(slab)),
            "Al_slabMin_sd_A": float(np.nanstd(slab)),
            "Al_slabMin_min_A": float(np.nanmin(slab)),
            "Al_slabMin_p05_A": float(np.nanpercentile(slab, 5)),
            "Al_slabMin_p50_A": float(np.nanpercentile(slab, 50)),
            "Al_slabMin_p95_A": float(np.nanpercentile(slab, 95)),
            "Al_height_mean_A": float(np.nanmean(height)),
            "Al_height_sd_A": float(np.nanstd(height)),
            "Al_nCl_mean": float(np.nanmean(ncl)),
            "Al_nCl_min": float(np.nanmin(ncl)),
            "Al_nCl_le1_frac": float(np.mean(ncl <= 1)),
            "front_lt3p2_frac": float(np.mean(slab < 3.2)),
            "near_lt4p0_frac": float(np.mean(slab < 4.0)),
            "near_lt5p0_frac": float(np.mean(slab < 5.0)),
            "near_lt6p0_frac": float(np.mean(slab < 6.0)),
        }
    )
    if np.isfinite(si).any():
        out["Al_SiMin_mean_A"] = float(np.nanmean(si))
        out["Al_SiMin_p50_A"] = float(np.nanpercentile(si, 50))
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    summaries = [summarize(label, spec) for label, spec in RUNS.items()]
    (OUT / "mlff_production_audit.json").write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    fieldnames = [
        "label",
        "role",
        "production_valid",
        "n_prod_rows",
        "teq_ps_per_segment",
        "Al_slabMin_mean_A",
        "Al_slabMin_sd_A",
        "Al_slabMin_min_A",
        "Al_slabMin_p05_A",
        "Al_slabMin_p50_A",
        "Al_slabMin_p95_A",
        "Al_height_mean_A",
        "Al_height_sd_A",
        "Al_nCl_mean",
        "Al_nCl_min",
        "front_lt3p2_frac",
        "near_lt4p0_frac",
        "near_lt5p0_frac",
        "near_lt6p0_frac",
        "Al_SiMin_mean_A",
        "Al_SiMin_p50_A",
        "exclusion_reason",
    ]
    with (OUT / "mlff_production_audit.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in summaries:
            writer.writerow(row)
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
