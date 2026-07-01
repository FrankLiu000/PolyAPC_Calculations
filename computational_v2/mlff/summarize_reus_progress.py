#!/usr/bin/env python3
"""Summarize live REUS window files and launcher log.

The summary is intentionally conservative: it does not declare a PMF converged,
only reports per-window coverage, CV/fmax ranges, exchange acceptance and cap/nan
counters from the live log.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import argparse
from pathlib import Path


WINDOW_RE = re.compile(r"window_z([0-9]+(?:\.[0-9]+)?)\.dat$")
CYCLE_RE = re.compile(
    r"cyc\s+(?P<cyc>\d+)/(?P<ncyc>\d+)\s+step\s+(?P<step>\d+)\s+fs\s+"
    r"exch_acc=(?P<acc>\d+)/(?P<trial>\d+).*cap=(?P<cap>\d+)\s+nan=(?P<nan>\d+)"
)
DEFAULT_FIELDS = [
    "window",
    "z0_A",
    "n_rows",
    "last_step_fs",
    "cv_min_A",
    "cv_max_A",
    "cv_last_A",
    "fmax_max_eV_A",
    "fmax_p95_eV_A",
    "n_fmax_gt20",
    "n_fmax_gt40",
]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root_pos", nargs="?", default=None)
    parser.add_argument("out_prefix_pos", nargs="?", default=None)
    parser.add_argument("log_path_pos", nargs="?", default=None)
    parser.add_argument("--outdir", dest="root_opt", default=None)
    parser.add_argument("--out-prefix", dest="out_prefix_opt", default=None)
    parser.add_argument("--results-dir", default=None)
    parser.add_argument("--tag", default="reus_dt05_progress")
    parser.add_argument("--log", dest="log_path_opt", default=None)
    args = parser.parse_args(argv)
    args.root = Path(args.root_opt or args.root_pos or "umb_poly_reus_dt05")
    if args.out_prefix_opt:
        args.out_prefix = Path(args.out_prefix_opt)
    elif args.results_dir:
        args.out_prefix = Path(args.results_dir) / args.tag
    else:
        args.out_prefix = Path(args.out_prefix_pos or "reus_dt05_progress")
    args.log_path = Path(args.log_path_opt or args.log_path_pos or "poly_reus_dt05_20260701.log")
    return args


def percentile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    values = sorted(values)
    return values[int(round((len(values) - 1) * q))]


def parse_window(path: Path) -> dict[str, float | int | str]:
    cvs: list[float] = []
    fmax: list[float] = []
    steps: list[int] = []
    for line in path.read_text().splitlines():
        if not line or not line[0].isdigit():
            continue
        fields = line.split()
        if len(fields) < 6:
            continue
        steps.append(int(float(fields[0])))
        cvs.append(float(fields[1]))
        fmax.append(float(fields[5]))
    z0 = float(WINDOW_RE.search(path.name).group(1))
    row: dict[str, float | int | str] = {
        "window": path.name,
        "z0_A": z0,
        "n_rows": len(steps),
        "last_step_fs": max(steps) if steps else 0,
    }
    if steps:
        row.update(
            {
                "cv_min_A": min(cvs),
                "cv_max_A": max(cvs),
                "cv_last_A": cvs[-1],
                "fmax_max_eV_A": max(fmax),
                "fmax_p95_eV_A": percentile(fmax, 0.95),
                "n_fmax_gt20": sum(v > 20 for v in fmax),
                "n_fmax_gt40": sum(v > 40 for v in fmax),
            }
        )
    return row


def parse_log(path: Path) -> dict[str, int | float | str | None]:
    latest = None
    if path.exists():
        for line in path.read_text(errors="replace").splitlines():
            match = CYCLE_RE.search(line)
            if match:
                latest = {k: int(v) for k, v in match.groupdict().items()}
    if not latest:
        return {
            "last_cycle": 0,
            "ncycles": None,
            "last_cycle_step_fs": 0,
            "exchange_acc": 0,
            "exchange_trials": 0,
            "exchange_acceptance": None,
            "cap_events": 0,
            "nan_events": 0,
        }
    trials = latest["trial"]
    return {
        "last_cycle": latest["cyc"],
        "ncycles": latest["ncyc"],
        "last_cycle_step_fs": latest["step"],
        "exchange_acc": latest["acc"],
        "exchange_trials": trials,
        "exchange_acceptance": latest["acc"] / trials if trials else None,
        "cap_events": latest["cap"],
        "nan_events": latest["nan"],
    }


def main() -> int:
    args = parse_args(sys.argv[1:])
    root = args.root
    out_prefix = args.out_prefix
    log_path = args.log_path
    windows = sorted(root.glob("window_z*.dat"), key=lambda p: float(WINDOW_RE.search(p.name).group(1)))
    rows = [parse_window(path) for path in windows]
    log_summary = parse_log(log_path)
    state_file = root / "reus_state.txt"
    running_file = root / "reus_running.txt"
    summary = {
        "out_dir": str(root),
        "n_windows": len(rows),
        "state_fs": int(state_file.read_text().strip()) if state_file.exists() else None,
        "running": running_file.read_text().strip() if running_file.exists() else None,
        "min_last_step_fs": min((int(r["last_step_fs"]) for r in rows), default=0),
        "max_last_step_fs": max((int(r["last_step_fs"]) for r in rows), default=0),
        "n_windows_ge_state": None,
        **log_summary,
    }
    if summary["state_fs"] is not None:
        summary["n_windows_ge_state"] = sum(int(r["last_step_fs"]) >= int(summary["state_fs"]) for r in rows)

    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    csv_path = out_prefix.with_suffix(".csv")
    json_path = out_prefix.with_suffix(".json")
    md_path = out_prefix.with_suffix(".md")
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else DEFAULT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(json.dumps({"summary": summary, "windows": rows}, indent=2) + "\n")
    exchange_acceptance = summary["exchange_acceptance"]
    exchange_text = f"{exchange_acceptance:.2%}" if exchange_acceptance is not None else "NA"
    lines = [
        "# REUS dt05 progress summary",
        "",
        f"- out_dir: `{root}`",
        f"- state_fs: {summary['state_fs']}",
        f"- running: {summary['running']}",
        f"- last completed cycle: {summary['last_cycle']} / {summary['ncycles']}",
        f"- exchange acceptance: {summary['exchange_acc']}/{summary['exchange_trials']} ({exchange_text})",
        f"- cap/nan events: {summary['cap_events']} / {summary['nan_events']}",
        f"- window last-step range: {summary['min_last_step_fs']}-{summary['max_last_step_fs']} fs",
        "",
        "This is a live health/progress summary, not a PMF convergence claim.",
        "",
        "| window | last fs | CV range / A | fmax max / eV A-1 | fmax p95 / eV A-1 | >20 | >40 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['window']} | {row['last_step_fs']} | "
            f"{row.get('cv_min_A', float('nan')):.3f}-{row.get('cv_max_A', float('nan')):.3f} | "
            f"{row.get('fmax_max_eV_A', float('nan')):.3f} | {row.get('fmax_p95_eV_A', float('nan')):.3f} | "
            f"{row.get('n_fmax_gt20', 0)} | {row.get('n_fmax_gt40', 0)} |"
        )
    md_path.write_text("\n".join(lines) + "\n")
    print(md_path)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
