#!/usr/bin/env python3
"""Build explicit deposited-Mg seed structures for post-gate T17 MLFF-MD.

These are controlled morphology/texture probes, not spontaneous Mg-plating
claims.  The added Mg atoms are written together with a 0-based index file so
the Mg(0002) texture analysis only counts the seeded deposited-Mg population.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from ase import Atom
from ase.io import read, write


NSLAB = 64
SYSTEMS = ("bare", "poly")


def frac_xy(xy: np.ndarray, cell: np.ndarray) -> np.ndarray:
    a2 = cell[:2, :2]
    return np.linalg.solve(a2.T, np.asarray(xy, dtype=float).T).T


def cart_xy(frac: np.ndarray, cell: np.ndarray) -> np.ndarray:
    return np.asarray(frac, dtype=float) @ cell[:2, :2]


def xy_delta(xy: np.ndarray, xy_ref: np.ndarray, cell: np.ndarray) -> np.ndarray:
    f = frac_xy(np.asarray(xy, dtype=float), cell)
    fr = frac_xy(np.asarray(xy_ref, dtype=float), cell)
    df = f - fr
    df -= np.round(df)
    return cart_xy(df, cell)


def dist_pbc_xy(pos: np.ndarray, pos_ref: np.ndarray, cell: np.ndarray) -> np.ndarray:
    dxy = xy_delta(pos[:2], pos_ref[:, :2], cell)
    dz = pos[2] - pos_ref[:, 2]
    return np.sqrt((dxy * dxy).sum(axis=1) + dz * dz)


def unique_rows(frac: np.ndarray, ndigits: int = 5) -> np.ndarray:
    wrapped = frac.copy() % 1.0
    rounded = np.round(wrapped, ndigits)
    _, idx = np.unique(rounded, axis=0, return_index=True)
    return wrapped[np.sort(idx)]


def registered_candidates(at) -> np.ndarray:
    """Generate on-lattice bridge/hollow candidates from the Mg slab registry."""
    cell = at.cell.array
    p = at.positions
    slab = np.arange(NSLAB)
    f = unique_rows(frac_xy(p[slab, :2], cell))
    pts: list[np.ndarray] = [x for x in f]

    xy = cart_xy(f, cell)
    n = len(f)
    for i in range(n):
        for j in range(i + 1, n):
            d = np.linalg.norm(xy_delta(xy[i], xy[j:j + 1], cell)[0])
            if 2.4 <= d <= 3.5:
                mid = f[i] + 0.5 * ((f[j] - f[i] + 0.5) % 1.0 - 0.5)
                pts.append(mid % 1.0)

    for i in range(n):
        neigh = []
        for j in range(n):
            if i == j:
                continue
            d = np.linalg.norm(xy_delta(xy[i], xy[j:j + 1], cell)[0])
            if 2.4 <= d <= 3.5:
                neigh.append(j)
        for a in range(len(neigh)):
            for b in range(a + 1, len(neigh)):
                j, k = neigh[a], neigh[b]
                dij = np.linalg.norm(xy_delta(xy[j], xy[k:k + 1], cell)[0])
                if 2.4 <= dij <= 3.8:
                    fj = f[i] + ((f[j] - f[i] + 0.5) % 1.0 - 0.5)
                    fk = f[i] + ((f[k] - f[i] + 0.5) % 1.0 - 0.5)
                    pts.append(((f[i] + fj + fk) / 3.0) % 1.0)
    return unique_rows(np.array(pts), ndigits=4)


def clearance(pos: np.ndarray, at, skip: set[int]) -> tuple[float, float, int]:
    sym = np.array(at.get_chemical_symbols())
    idx = np.array([i for i in range(len(at)) if i not in skip], dtype=int)
    if len(idx) == 0:
        return 99.0, 99.0, -1
    d = dist_pbc_xy(pos, at.positions[idx], at.cell.array)
    cut = np.where(sym[idx] == "H", 1.35, 1.95)
    margin = d - cut
    imin = int(np.argmin(margin))
    return float(margin[imin]), float(d[imin]), int(idx[imin])


def candidate_record(at, fxy: np.ndarray, z_offset: float) -> dict | None:
    cell = at.cell.array
    p = at.positions
    slab = np.arange(NSLAB)
    xy = cart_xy(fxy, cell)
    dxy = np.linalg.norm(xy_delta(xy, p[slab, :2], cell), axis=1)
    near = slab[np.argsort(dxy)[:4]]
    z_base = float(p[near, 2].max())
    pos = np.array([xy[0], xy[1], z_base + z_offset], dtype=float)
    dslab = float(dist_pbc_xy(pos, p[slab], cell).min())
    if not (2.25 <= dslab <= 3.45):
        return None
    margin, dnon, inon = clearance(pos, at, skip=set(slab))
    if margin < 0.0:
        return None
    score = margin - abs(dslab - 2.65) * 0.2
    return {
        "position_A": [float(x) for x in pos],
        "frac_xy": [float(x) for x in (fxy % 1.0)],
        "slab_min_A": float(dslab),
        "nearest_nonslab_A": float(dnon),
        "nearest_nonslab_index0": int(inon),
        "clearance_margin_A": float(margin),
        "site_score": float(score),
    }


def pick_matched_positions(ats: dict[str, object], n_add: int, z_offset: float) -> dict[str, list[dict]]:
    """Pick the same fractional surface sites for bare and poly."""
    cand_frac = unique_rows(
        np.vstack([registered_candidates(ats[system]) for system in SYSTEMS]),
        ndigits=4,
    )
    scored = []
    for fxy in cand_frac:
        recs = {system: candidate_record(ats[system], fxy, z_offset) for system in SYSTEMS}
        if any(rec is None for rec in recs.values()):
            continue
        score = min(float(rec["site_score"]) for rec in recs.values())
        margin = min(float(rec["clearance_margin_A"]) for rec in recs.values())
        scored.append((score, margin, fxy, recs))
    scored.sort(key=lambda x: x[0], reverse=True)

    chosen: list[tuple] = []
    cell = ats["bare"].cell.array
    for cand in scored:
        fxy = cand[2]
        xy = cart_xy(fxy, cell)
        if chosen:
            prev_xy = np.array([cart_xy(c[2], cell) for c in chosen])
            pseudo_pos = np.array([xy[0], xy[1], 0.0])
            pseudo_prev = np.column_stack([prev_xy, np.zeros(len(prev_xy))])
            if dist_pbc_xy(pseudo_pos, pseudo_prev, cell).min() < 2.75:
                continue
        chosen.append(cand)
        if len(chosen) == n_add:
            break
    if len(chosen) < n_add:
        raise RuntimeError(f"only found {len(chosen)} matched Mg-deposit sites; requested {n_add}")

    return {system: [cand[3][system] for cand in chosen] for system in SYSTEMS}


def clean_atoms(system: str):
    here = Path(__file__).resolve().parent
    start = here / f"{system}_start.xyz"
    at = read(start)
    for arr in ("forces", "momenta"):
        if arr in at.arrays:
            del at.arrays[arr]
    at.calc = None
    return at


def build(system: str, at, positions: list[dict], n_add: int, z_offset: float, overwrite: bool) -> dict:
    here = Path(__file__).resolve().parent
    start = here / f"{system}_start.xyz"
    out_xyz = here / f"{system}_mgdep_start.xyz"
    out_idx = here / f"{system}_mgdep_indices0.txt"
    out_manifest = here / f"{system}_mgdep_manifest.json"
    if not overwrite and (out_xyz.exists() or out_idx.exists() or out_manifest.exists()):
        raise FileExistsError(f"{system}: mgdep outputs already exist; pass --overwrite")

    indices = []
    for rec in positions:
        at.append(Atom("Mg", rec["position_A"]))
        indices.append(len(at) - 1)
    at.info["config_type"] = f"{at.info.get('config_type', 't17')}_mgdep_texture_probe"
    at.info["mgdep_seeded_count"] = n_add
    write(out_xyz, at)
    np.savetxt(out_idx, np.array(indices, dtype=int), fmt="%d")

    manifest = {
        "system": system,
        "source_start": str(start),
        "output_start": str(out_xyz),
        "index_file_0based": str(out_idx),
        "n_seeded_deposited_mg": n_add,
        "z_offset_A": z_offset,
        "new_indices0": indices,
        "positions": positions,
        "matched_fractional_sites": True,
        "interpretation": "controlled deposited-Mg texture probe; not spontaneous Mg plating",
    }
    out_manifest.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main(argv: list[str]) -> int:
    n_add = 4
    z_offset = 2.65
    overwrite = False
    args = list(argv)
    if "--overwrite" in args:
        overwrite = True
        args.remove("--overwrite")
    if args:
        n_add = int(args.pop(0))
    if args:
        z_offset = float(args.pop(0))
    if args:
        print(__doc__)
        return 2

    ats = {system: clean_atoms(system) for system in SYSTEMS}
    positions = pick_matched_positions(ats, n_add=n_add, z_offset=z_offset)
    manifests = [build(system, ats[system], positions[system], n_add, z_offset, overwrite) for system in SYSTEMS]
    for m in manifests:
        print(
            f"{m['system']}: wrote {m['output_start']} with indices {m['new_indices0']} "
            f"(n={m['n_seeded_deposited_mg']})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
