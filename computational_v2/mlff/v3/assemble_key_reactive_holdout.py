#!/usr/bin/env python3
"""Assemble an r8 MLFF dataset with explicit key-reactive holdout frames.

The original exact-config stratification puts one-off reactive labels
(`dep_bare_h20`, `react_bare_clstrip_0.50`, etc.) entirely in train.  That is
fine for coverage, but it cannot prove publication-grade transfer on Mg/Al
co-deposition chemistry.  This assembler groups those one-off labels into
reaction families and reserves val/test frames before training.

Usage:
    assemble_key_reactive_holdout.py <incoming_dir> <out_dir>
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
import sys
from pathlib import Path

import numpy as np
from ase.io import read, write


SEED = 20260701
ELEM_OK = {"Mg", "Al", "Cl", "O", "C", "H", "Si"}
KEY_GROUPS = {"al_bare_nearsurface", "dep_bare", "react_bare_clstrip"}


def geom_hash(at) -> str:
    payload = (
        "".join(at.get_chemical_symbols()).encode()
        + np.round(np.asarray(at.cell), 3).tobytes()
        + np.round(at.get_positions(), 3).tobytes()
    )
    return hashlib.md5(payload).hexdigest()


def config_type(at) -> str:
    return str(at.info.get("config_type", "unknown"))


def split_group(ct: str) -> str:
    if ct == "al_bare_nearsurface":
        return "al_bare_nearsurface"
    if ct.startswith("dep_bare"):
        return "dep_bare"
    if ct.startswith("react_bare_clstrip"):
        return "react_bare_clstrip"
    return ct


def has_forces(at) -> bool:
    if "forces" in at.arrays:
        return True
    try:
        at.get_forces()
        return True
    except Exception:
        return False


def read_frames(incoming: Path):
    frames = []
    seen = set()
    dropped = {"duplicate": 0, "no_forces": 0, "bad_read": 0, "bad_elements": 0}
    for path in sorted(incoming.glob("*.xyz")):
        try:
            atoms = read(path, index=":")
        except Exception:
            dropped["bad_read"] += 1
            continue
        for at in atoms:
            els = set(at.get_chemical_symbols())
            if not els <= ELEM_OK:
                dropped["bad_elements"] += 1
                continue
            if not has_forces(at):
                dropped["no_forces"] += 1
                continue
            h = geom_hash(at)
            if h in seen:
                dropped["duplicate"] += 1
                continue
            seen.add(h)
            at.info.setdefault("config_type", config_type(at))
            at.info["split_group"] = split_group(config_type(at))
            frames.append(at)
    return frames, dropped


def allocate(groups: dict[str, list]) -> tuple[list, list, list, list[dict]]:
    rng = random.Random(SEED)
    train, val, test = [], [], []
    rows = []
    for group, frames in sorted(groups.items()):
        frames = list(frames)
        rng.shuffle(frames)
        n = len(frames)
        if group in KEY_GROUPS and n >= 6:
            n_test = max(2, int(round(0.25 * n)))
            n_val = max(1, int(round(0.125 * n)))
        else:
            n_test = int(0.10 * n)
            n_val = int(0.10 * n)
        n_test = min(n_test, max(0, n - 2))
        n_val = min(n_val, max(0, n - n_test - 1))
        test_part = frames[:n_test]
        val_part = frames[n_test:n_test + n_val]
        train_part = frames[n_test + n_val:]
        test.extend(test_part)
        val.extend(val_part)
        train.extend(train_part)
        rows.append(
            {
                "split_group": group,
                "n_total": n,
                "n_train": len(train_part),
                "n_val": len(val_part),
                "n_test": len(test_part),
                "config_types": ";".join(sorted({config_type(at) for at in frames})),
            }
        )
    return train, val, test, rows


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    incoming = Path(argv[0])
    out = Path(argv[1])
    out.mkdir(parents=True, exist_ok=True)
    frames, dropped = read_frames(incoming)
    groups: dict[str, list] = {}
    for at in frames:
        groups.setdefault(str(at.info["split_group"]), []).append(at)
    train, val, test, rows = allocate(groups)
    write(out / "train.xyz", train)
    write(out / "val.xyz", val)
    write(out / "test_key.xyz", test)
    with (out / "split_report.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["split_group", "n_total", "n_train", "n_val", "n_test", "config_types"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    report = {
        "incoming": str(incoming),
        "out": str(out),
        "seed": SEED,
        "n_unique_frames": len(frames),
        "splits": {"train": len(train), "val": len(val), "test_key": len(test)},
        "dropped": dropped,
        "key_groups": {row["split_group"]: row for row in rows if row["split_group"] in KEY_GROUPS},
    }
    (out / "split_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
