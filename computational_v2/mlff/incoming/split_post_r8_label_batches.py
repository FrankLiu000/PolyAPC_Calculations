#!/usr/bin/env python3
"""Split mixed post-r8 DFT candidate frames into CP2K label batches.

``label_forces.py`` expects one Natoms/charge/cell combination per run.  The
post-r8 queue may contain bare, poly, and Mg-deposit probes with different atom
counts, so this helper writes one scaffold xyz per compatible group plus a TSV
manifest consumed by ``submit_post_r8_label.sbatch``.
"""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path


LATTICE_RE = re.compile(r'Lattice="([^"]+)"')
CHARGE_RE = re.compile(r"(?:^|\s)charge=([-+0-9.eE]+)")


def frames(path):
    if not path.exists() or path.stat().st_size == 0:
        return
    with path.open() as handle:
        while True:
            line = handle.readline()
            if not line:
                return
            if not line.strip():
                continue
            try:
                nat = int(line.split()[0])
            except (ValueError, IndexError):
                return
            comment = handle.readline()
            atoms = [handle.readline() for _ in range(nat)]
            if len(atoms) != nat or any(not atom for atom in atoms):
                return
            yield nat, comment.rstrip("\n"), atoms


def lattice_csv(comment):
    match = LATTICE_RE.search(comment)
    if not match:
        raise ValueError("missing Lattice field")
    return ",".join(match.group(1).split())


def charge(comment):
    match = CHARGE_RE.search(comment)
    if not match:
        return "0"
    val = float(match.group(1))
    if abs(val - round(val)) < 1e-8:
        return str(int(round(val)))
    return f"{val:g}"


def gid(nat, chg, lat):
    digest = hashlib.sha1(lat.encode("utf-8")).hexdigest()[:8]
    clean_charge = chg.replace("+", "p").replace("-", "m").replace(".", "p")
    return f"N{nat}_q{clean_charge}_lat{digest}"


def main(argv):
    src = Path(argv[0]) if argv else Path("post_r8_dft_candidates.xyz")
    outdir = Path(argv[1]) if len(argv) > 1 else Path("post_r8_label_batches")
    outdir.mkdir(parents=True, exist_ok=True)
    groups = {}
    errors = []
    for idx, frame in enumerate(frames(src) or []):
        nat, comment, atoms = frame
        try:
            lat = lattice_csv(comment)
            chg = charge(comment)
        except ValueError as exc:
            errors.append({"frame": idx, "error": str(exc)})
            continue
        groups.setdefault((nat, chg, lat), []).append((comment, atoms))

    manifest = []
    for (nat, chg, lat), items in sorted(groups.items(), key=lambda x: (x[0][0], x[0][1], x[0][2])):
        group_id = gid(nat, chg, lat)
        scaffold = outdir / f"{group_id}.xyz"
        labeled = outdir / f"{group_id}_labeled.xyz"
        with scaffold.open("w") as handle:
            for comment, atoms in items:
                handle.write(f"{nat}\n{comment}\n")
                handle.writelines(atoms)
        manifest.append(
            {
                "group_id": group_id,
                "natoms": nat,
                "charge": chg,
                "lattice_csv": lat,
                "n_frames": len(items),
                "n_slab": 64,
                "scaffold": str(scaffold),
                "labeled": str(labeled),
            }
        )

    tsv = outdir / "manifest.tsv"
    with tsv.open("w", newline="") as handle:
        fields = ["group_id", "natoms", "charge", "lattice_csv", "n_frames", "n_slab", "scaffold", "labeled"]
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(manifest)
    (outdir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (outdir / "split_errors.json").write_text(json.dumps(errors, indent=2) + "\n", encoding="utf-8")
    report = [
        "# post-r8 CP2K label batch split",
        "",
        f"- source: `{src}`",
        f"- groups: {len(manifest)}",
        f"- errors: {len(errors)}",
        "",
    ]
    if manifest:
        report += ["| group | Natoms | charge | frames |", "|---|---:|---:|---:|"]
        for row in manifest:
            report.append(f"| {row['group_id']} | {row['natoms']} | {row['charge']} | {row['n_frames']} |")
    else:
        report.append("No frames were available to split.")
    (outdir / "SPLIT_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(tsv)
    print(f"groups={len(manifest)} errors={len(errors)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
