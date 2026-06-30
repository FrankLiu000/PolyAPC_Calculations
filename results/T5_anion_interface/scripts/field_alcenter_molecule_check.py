#!/usr/bin/env python3
"""Fixed-face Al-center and molecule-level checks for T5 field MD.

This is a conservative follow-up to the v3.6 all-ANI-atom density analysis.
It keeps the same reference slab faces, but reports redox-relevant Al centers,
Al/Cl atoms, and unique ANI molecule contact events.  The trajectory is streamed
once per system while accumulating all time windows and layer cutoffs, to avoid
large memory use on the Windows/WSL workstation.
"""
from __future__ import annotations

import csv
import glob
import os
import sys
from pathlib import Path

import MDAnalysis as mda


STORY = Path(os.environ.get("STORY_T5", "/lyz/Claude_workplace/polyAPC/storyT5"))
OUT = Path(__file__).resolve().parents[1]
SYSTEMS = ["bare_t21", "poly_t21"]
T0_WINDOWS_NS = [50.0, 130.0]
LAYERS_NM = [0.6, 1.0, 1.5]
MIN_MEM_GB = float(os.environ.get("T5_POST_MIN_MEM_GB", "8"))


def require_mem_gb(min_gb: float) -> None:
    with open("/proc/meminfo") as handle:
        for line in handle:
            if line.startswith("MemAvailable:"):
                avail_gb = float(line.split()[1]) / 1024.0 / 1024.0
                if avail_gb < min_gb:
                    raise SystemExit(
                        f"Refusing to start: WSL MemAvailable={avail_gb:.1f} GiB < required {min_gb:.1f} GiB"
                    )
                return


def reference_faces(gro: Path) -> tuple[float, float]:
    ref = mda.Universe(str(gro))
    z_nm = sorted(ref.select_atoms("resname MGE").positions[:, 2] / 10.0)
    half = len(z_nm) // 2
    return max(z_nm[:half]), min(z_nm[half:])


def trajectories(sysdir: str) -> list[str]:
    base = STORY / "sym" / sysdir / "field.xtc"
    parts = sorted(glob.glob(str(base).replace(".xtc", ".part*.xtc")))
    paths = [str(path) for path in [base] + [Path(part) for part in parts] if Path(path).exists()]
    if not paths:
        raise FileNotFoundError(f"no field trajectory files found for {sysdir}")
    return paths


def in_layer(z_nm, s1max: float, s2min: float, layer_nm: float):
    face_a = (z_nm > s1max) & (z_nm < s1max + layer_nm)
    face_b = (z_nm < s2min) & (z_nm > s2min - layer_nm)
    return face_a, face_b


def empty_sums() -> dict[str, float]:
    keys = [
        "all_atoms_A",
        "all_atoms_B",
        "al_center_A",
        "al_center_B",
        "reactive_atoms_A",
        "reactive_atoms_B",
        "mol_any_atom_A",
        "mol_any_atom_B",
        "mol_reactive_atom_A",
        "mol_reactive_atom_B",
        "nframes",
    ]
    return {key: 0.0 for key in keys}


def analyze_system(sysdir: str) -> list[dict[str, float | str | int]]:
    gro = STORY / "sym" / sysdir / "em3dc.gro"
    s1max, s2min = reference_faces(gro)
    u = mda.Universe(str(gro), trajectories(sysdir))
    area_nm2 = u.dimensions[0] * u.dimensions[1] / 100.0

    ani = u.select_atoms("resname ANI")
    al = u.select_atoms("resname ANI and name Al")
    reactive = u.select_atoms("resname ANI and (name Al or name Cl1 or name Cl2)")
    residues = list(ani.residues)
    residue_reactive = [res.atoms.select_atoms("name Al or name Cl1 or name Cl2") for res in residues]

    accum: dict[tuple[float, float], dict[str, float]] = {
        (t0_ns, layer_nm): empty_sums() for t0_ns in T0_WINDOWS_NS for layer_nm in LAYERS_NM
    }
    min_t0 = min(T0_WINDOWS_NS)
    for ts in u.trajectory:
        time_ns = ts.time / 1000.0
        if time_ns < min_t0:
            continue
        for t0_ns in T0_WINDOWS_NS:
            if time_ns < t0_ns:
                continue
            for layer_nm in LAYERS_NM:
                sums = accum[(t0_ns, layer_nm)]
                all_a, all_b = in_layer(ani.positions[:, 2] / 10.0, s1max, s2min, layer_nm)
                al_a, al_b = in_layer(al.positions[:, 2] / 10.0, s1max, s2min, layer_nm)
                re_a, re_b = in_layer(reactive.positions[:, 2] / 10.0, s1max, s2min, layer_nm)
                sums["all_atoms_A"] += int(all_a.sum())
                sums["all_atoms_B"] += int(all_b.sum())
                sums["al_center_A"] += int(al_a.sum())
                sums["al_center_B"] += int(al_b.sum())
                sums["reactive_atoms_A"] += int(re_a.sum())
                sums["reactive_atoms_B"] += int(re_b.sum())

                for res, re_atoms in zip(residues, residue_reactive):
                    ra, rb = in_layer(res.atoms.positions[:, 2] / 10.0, s1max, s2min, layer_nm)
                    rra, rrb = in_layer(re_atoms.positions[:, 2] / 10.0, s1max, s2min, layer_nm)
                    sums["mol_any_atom_A"] += int(ra.any())
                    sums["mol_any_atom_B"] += int(rb.any())
                    sums["mol_reactive_atom_A"] += int(rra.any())
                    sums["mol_reactive_atom_B"] += int(rrb.any())
                sums["nframes"] += 1

    rows: list[dict[str, float | str | int]] = []
    for (t0_ns, layer_nm), sums in accum.items():
        nframes = int(sums["nframes"])
        if nframes == 0:
            continue
        row: dict[str, float | str | int] = {
            "system": sysdir,
            "t0_ns": t0_ns,
            "nframes": nframes,
            "area_nm2": area_nm2,
            "faceA_ref_nm": s1max,
            "faceB_ref_nm": s2min,
            "layer_nm": layer_nm,
        }
        for key, value in sums.items():
            if key == "nframes":
                continue
            row[key + "_density_nm2"] = value / (area_nm2 * nframes)
        rows.append(row)
    return rows


def row_metrics(row: dict[str, float | str | int]) -> list[dict[str, float | str | int]]:
    metrics = [
        ("all_atoms", "all ANI atoms / nm2"),
        ("al_center", "Al centers / nm2"),
        ("reactive_atoms", "Al+Cl atoms / nm2"),
        ("mol_any_atom", "ANI molecules with any atom in layer / nm2"),
        ("mol_reactive_atom", "ANI molecules with Al/Cl in layer / nm2"),
    ]
    rows = []
    for key, label in metrics:
        a = float(row[f"{key}_A_density_nm2"])
        b = float(row[f"{key}_B_density_nm2"])
        rows.append(
            {
                "system": row["system"],
                "window": f"{float(row['t0_ns']):.0f}-200ns",
                "layer_nm": row["layer_nm"],
                "metric": key,
                "metric_label": label,
                "faceA_density_nm2": a,
                "faceB_cathode_density_nm2": b,
                "B_over_A": b / a if a else float("nan"),
                "nframes": row["nframes"],
            }
        )
    return rows


def main() -> int:
    require_mem_gb(MIN_MEM_GB)
    raw_rows: list[dict[str, float | str | int]] = []
    for sysdir in SYSTEMS:
        print(f"[field_check] streaming {sysdir}", file=sys.stderr, flush=True)
        raw_rows.extend(analyze_system(sysdir))
    metric_rows = [metric for raw in raw_rows for metric in row_metrics(raw)]

    raw_path = OUT / "field_alcenter_molecule_check_raw.csv"
    with raw_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(raw_rows[0].keys()))
        writer.writeheader()
        writer.writerows(raw_rows)

    metrics_path = OUT / "field_alcenter_molecule_check.csv"
    with metrics_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(metric_rows[0].keys()))
        writer.writeheader()
        writer.writerows(metric_rows)

    print(metrics_path)
    for row in metric_rows:
        print(
            f"{row['system']} {row['window']} {row['metric']} layer={row['layer_nm']}nm: "
            f"A={row['faceA_density_nm2']:.4f} B(cathode)={row['faceB_cathode_density_nm2']:.4f} "
            f"B/A={row['B_over_A']:.2f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
