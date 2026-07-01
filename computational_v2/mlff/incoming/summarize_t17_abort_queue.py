#!/usr/bin/env python3
"""Summarize T17 guarded-abort frames for DFT active-learning requests."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
from ase.io import read


def main() -> int:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("t17_bare_seed2026070101_abort_unlabeled.xyz")
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".geom_summary.csv")
    frames = read(str(src), ":")
    rows = []
    for i, at in enumerate(frames):
        sym = np.array(at.get_chemical_symbols())
        pos = at.get_positions()
        al = int(np.where(sym == "Al")[0][0])
        slab = np.arange(64)
        cl = np.where(sym == "Cl")[0]
        d_mg = np.linalg.norm(pos[slab] - pos[al], axis=1)
        d_cl = np.linalg.norm(pos[cl] - pos[al], axis=1)
        nearest_cl = np.sort(d_cl)[:2]
        rows.append(
            {
                "frame": i,
                "source_md_step": int(at.info.get("source_md_step", -1)),
                "source_time_ps": float(at.info.get("source_step_fs", 0.0)) / 1000.0,
                "al_slab_min_A": float(d_mg.min()),
                "n_mg_lt_3p2": int((d_mg < 3.2).sum()),
                "n_cl_lt_2p8": int((d_cl < 2.8).sum()),
                "al_cl_min_A": float(d_cl.min()),
                "al_cl_second_A": float(nearest_cl[-1]),
            }
        )
    with out.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(out)
    for row in rows:
        print(
            "{frame},{source_time_ps:.3f},{al_slab_min_A:.3f},{n_mg_lt_3p2},"
            "{n_cl_lt_2p8},{al_cl_min_A:.3f},{al_cl_second_A:.3f}".format(**row)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
