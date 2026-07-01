#!/usr/bin/env python3
"""Mg(0002) texture proxy from AIMD/MLFF XYZ trajectories.

The script intentionally excludes the initial Mg slab from the texture metric.
It only analyzes Mg atoms above the slab that are close enough to the electrode
to be plausible deposited Mg. If no such atoms exist, it reports that the
trajectory cannot address plated-Mg texture rather than producing a slab-driven
false positive.

Usage:
    mg_texture_from_xyz.py <trajectory.xyz> <out_prefix> [tail_frac] [deposited_index_file|--auto-detect] [--nslab N]
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
from ase.io import read


A_MG = 3.209
C_MG = 5.211
D_0002 = C_MG / 2.0
Q_0002 = 2.0 * np.pi / D_0002
Q_10M10 = 2.0 * np.pi / (A_MG * np.sqrt(3.0) / 2.0)
MG_NEAR_CUTOFF = 3.7
MG_METAL_COORD_CUTOFF = 3.75
MIN_METAL_COORD = 3
SOLV_CUTOFF = 3.0
MAX_SOLVATION_NEIGHBORS = 1
SLAB_GAP_MIN_A = 3.8


def slab_indices(at, nslab: int | None = None) -> tuple[np.ndarray, float]:
    sym = np.array(at.get_chemical_symbols())
    if nslab is not None:
        slab = np.arange(nslab, dtype=int)
        slab = slab[slab < len(sym)]
        slab = slab[sym[slab] == "Mg"]
        if len(slab):
            return slab, float(at.get_positions()[slab, 2].max())
    mg = np.where(sym == "Mg")[0]
    z = at.get_positions()[mg, 2]
    order = np.argsort(z)
    z_sorted = z[order]
    if len(z_sorted) < 4:
        return mg, float(z_sorted.max()) if len(z_sorted) else 0.0
    gaps = np.diff(z_sorted)
    gap = int(np.argmax(gaps))
    if gaps[gap] < SLAB_GAP_MIN_A:
        # Dense Mg-only slab or no electrolyte gap; treat lowest half as substrate.
        gap = len(z_sorted) // 2 - 1
    slab = mg[order[: gap + 1]]
    return slab, float(at.get_positions()[slab, 2].max())


def select_deposited_mg(at, slab: np.ndarray, slab_top: float, explicit: np.ndarray | None, auto_detect: bool) -> np.ndarray:
    sym = np.array(at.get_chemical_symbols())
    pos = at.get_positions()
    mg = np.where(sym == "Mg")[0]
    if explicit is not None:
        return np.array([idx for idx in explicit if idx in set(mg) and idx not in set(slab)], dtype=int)
    if not auto_detect:
        return np.array([], dtype=int)
    solv = np.where((sym == "O") | (sym == "Cl"))[0]
    free = np.array([idx for idx in mg if idx not in set(slab)], dtype=int)
    if len(free) == 0:
        return free
    # Candidate plated Mg: above the slab and in direct/near contact with the Mg electrode
    # or an already-contacting deposited Mg atom. This avoids counting solvated Mg cations.
    above = free[pos[free, 2] > slab_top - 0.5]
    if len(above) == 0:
        return above
    dslab = np.linalg.norm(pos[above, None, :] - pos[slab][None, :, :], axis=2).min(axis=1)
    deposited = set(above[dslab < MG_NEAR_CUTOFF].tolist())
    changed = True
    while changed and deposited:
        changed = False
        dep = np.array(sorted(deposited), dtype=int)
        remaining = np.array([idx for idx in above if idx not in deposited], dtype=int)
        if len(remaining) == 0:
            break
        ddep = np.linalg.norm(pos[remaining, None, :] - pos[dep][None, :, :], axis=2).min(axis=1)
        for idx in remaining[ddep < MG_NEAR_CUTOFF]:
            deposited.add(int(idx))
            changed = True
    if not deposited:
        return np.array([], dtype=int)
    # Plated Mg must look metal-like, not like solvated Mg2+ in the double layer.
    # A surface adatom has at least three Mg neighbours from the slab/island and
    # should not retain a full O/Cl solvation shell.
    keep = []
    metal_pool = np.concatenate([slab, np.array(sorted(deposited), dtype=int)])
    for idx in sorted(deposited):
        d_mg = np.linalg.norm(pos[metal_pool] - pos[idx], axis=1)
        metal_coord = int(((d_mg < MG_METAL_COORD_CUTOFF) & (d_mg > 1e-6)).sum())
        solv_coord = int((np.linalg.norm(pos[solv] - pos[idx], axis=1) < SOLV_CUTOFF).sum()) if len(solv) else 0
        if metal_coord >= MIN_METAL_COORD and solv_coord <= MAX_SOLVATION_NEIGHBORS:
            keep.append(idx)
    return np.array(keep, dtype=int)


def intensity(pos: np.ndarray, qvec: np.ndarray) -> float:
    if len(pos) == 0:
        return np.nan
    phase = pos @ qvec
    amp = np.exp(1j * phase).sum()
    return float((amp.conjugate() * amp).real / (len(pos) ** 2))


def frame_metrics(at, slab: np.ndarray, slab_top: float, explicit: np.ndarray | None, auto_detect: bool) -> dict[str, float | int]:
    pos = at.get_positions()
    dep = select_deposited_mg(at, slab, slab_top, explicit, auto_detect)
    p = pos[dep]
    if len(p) < 3:
        return {
            "n_deposited_mg": len(p),
            "z_order_0002": np.nan,
            "I0002_z": np.nan,
            "I10m10_xy": np.nan,
            "texture_I0002_over_I10m10": np.nan,
            "mean_height_A": np.nan,
        }
    zphase = np.exp(1j * 2.0 * np.pi * (p[:, 2] - slab_top) / D_0002)
    z_order = float(abs(zphase.mean()))
    i0002 = intensity(p, np.array([0.0, 0.0, Q_0002]))
    qdirs = []
    for ang in np.linspace(0, 2 * np.pi, 6, endpoint=False):
        qdirs.append(np.array([np.cos(ang) * Q_10M10, np.sin(ang) * Q_10M10, 0.0]))
    i10 = float(np.nanmean([intensity(p, q) for q in qdirs]))
    return {
        "n_deposited_mg": len(p),
        "z_order_0002": z_order,
        "I0002_z": i0002,
        "I10m10_xy": i10,
        "texture_I0002_over_I10m10": i0002 / i10 if i10 > 0 else np.nan,
        "mean_height_A": float((p[:, 2] - slab_top).mean()),
    }


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    traj = Path(argv[0])
    out = Path(argv[1])
    tail = float(argv[2]) if len(argv) > 2 else 0.5
    explicit = None
    auto_detect = False
    nslab = None
    mode = "explicit-index-required"
    args = list(argv[3:])
    while args:
        arg = args.pop(0)
        if arg == "--auto-detect":
            auto_detect = True
            mode = "auto-detect"
        elif arg == "--nslab":
            if not args:
                raise ValueError("--nslab requires an integer")
            nslab = int(args.pop(0))
        else:
            explicit = np.loadtxt(arg, dtype=int, ndmin=1)
            mode = f"explicit-index-file:{arg}"
    atoms = read(traj, index=":")
    start = int(len(atoms) * (1.0 - tail))
    atoms = atoms[start:]
    slab, slab_top = slab_indices(atoms[0], nslab=nslab)
    rows = []
    for i, at in enumerate(atoms):
        rec = frame_metrics(at, slab, slab_top, explicit, auto_detect)
        rec["frame"] = i + start
        rows.append(rec)
    out.parent.mkdir(parents=True, exist_ok=True)
    csv_path = out.with_suffix(".csv")
    with csv_path.open("w", newline="") as handle:
        fields = ["frame", "n_deposited_mg", "z_order_0002", "I0002_z", "I10m10_xy", "texture_I0002_over_I10m10", "mean_height_A"]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    n = np.array([r["n_deposited_mg"] for r in rows], dtype=float)
    tex = np.array([r["texture_I0002_over_I10m10"] for r in rows], dtype=float)
    zord = np.array([r["z_order_0002"] for r in rows], dtype=float)
    valid = np.isfinite(tex)
    summary = [
        "# Mg texture proxy",
        "",
        f"- trajectory: `{traj}`",
        f"- analyzed_frames: {len(rows)} (tail_frac={tail})",
        f"- selection_mode: {mode}",
        f"- nslab_override: {nslab if nslab is not None else 'auto'}",
        f"- slab_top_A: {slab_top:.3f}",
        f"- deposited Mg/frame: mean={np.nanmean(n):.2f}, max={np.nanmax(n):.0f}",
    ]
    if valid.any():
        summary += [
            f"- z_order_0002: mean={np.nanmean(zord):.3f}",
            f"- I0002/I10m10: mean={np.nanmean(tex):.3f}",
            "",
            "Interpretation: larger z_order_0002 and I0002/I10m10 indicate stronger Mg(0002)-aligned layering in newly deposited Mg.",
        ]
    else:
        summary += [
            "",
            "No sufficient deposited-Mg population was detected. This trajectory should not be used to claim Mg(0002) texture.",
        ]
    md_path = out.with_suffix(".md")
    md_path.write_text("\n".join(summary) + "\n")
    print(md_path)
    print(csv_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
