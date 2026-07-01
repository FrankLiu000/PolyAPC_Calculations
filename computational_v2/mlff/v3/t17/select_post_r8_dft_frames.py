#!/usr/bin/env python3
"""Select post-r8 MLFF-MD candidate frames for CPU DFT/AIMD validation.

Only completed gated post-r8 runs (``*_done.json``) are considered.  The output
queue is an extxyz file with provenance in ``Atoms.info`` so CPU-side labelling
can validate any MLFF-observed Al contact/dechlorination or Mg-texture event.
"""
from __future__ import annotations

import csv
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from ase.io import read, write


REPO = Path(__file__).resolve().parents[4]
WORK = REPO / "computational_v2" / "mlff" / "v3" / "t17"
INCOMING = REPO / "computational_v2" / "mlff" / "incoming"
TEXTURE_DIR = REPO / "results" / "T13_nucleation" / "mgdep_texture_r8"
SEED_AUDIT_DIR = REPO / "results" / "T13_nucleation" / "mgdep_seed_audit"
OUTDIR = REPO / "results" / "T17_reactive" / "post_r8_dft_frame_queue"
LABEL_RE = re.compile(r"^(bare|poly)_(r8neutral|r8mgdep)_seed(\d+)_([0-9.]+)ps$")
SAVE_STRIDE_STEPS = 200


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def fval(row: dict[str, str], key: str) -> float:
    try:
        val = float(row.get(key, "nan"))
    except ValueError:
        return math.nan
    return val if math.isfinite(val) else math.nan


def completed_labels() -> list[str]:
    labels = []
    for done in sorted(WORK.glob("*_done.json")):
        label = done.name[: -len("_done.json")]
        if LABEL_RE.match(label):
            labels.append(label)
    return labels


def label_parts(label: str) -> dict[str, str]:
    match = LABEL_RE.match(label)
    if not match:
        raise ValueError(label)
    system, tag, seed, ps = match.groups()
    return {"system": system, "tag": tag, "seed": seed, "ps": ps}


def step_to_frame_index(step: int, n_frames: int) -> int:
    idx = int(round(step / SAVE_STRIDE_STEPS))
    return max(0, min(n_frames - 1, idx))


def add_candidate(cands: list[dict], label: str, reason: str, cv_row: dict[str, str], priority: float) -> None:
    step = int(round(fval(cv_row, "step")))
    cands.append(
        {
            "label": label,
            "reason": reason,
            "md_step": step,
            "t_ps": fval(cv_row, "t_ps"),
            "Al_slabMin_A": fval(cv_row, "Al_slabMin_A"),
            "Al_height_A": fval(cv_row, "Al_height_A"),
            "Al_nCl": fval(cv_row, "Al_nCl"),
            "Al_nO": fval(cv_row, "Al_nO"),
            "priority": priority,
        }
    )


def cv_candidates(label: str, max_per_reason: int) -> list[dict]:
    rows = read_csv(WORK / f"{label}_cv.csv")
    rows = [row for row in rows if math.isfinite(fval(row, "Al_slabMin_A"))]
    if not rows:
        return []
    cands: list[dict] = []

    codep = [row for row in rows if fval(row, "Al_slabMin_A") <= 3.2 and fval(row, "Al_nCl") <= 1.0]
    codep.sort(key=lambda r: (fval(r, "Al_slabMin_A"), fval(r, "Al_nCl")))
    for row in codep[:max_per_reason]:
        add_candidate(cands, label, "codeposition_proxy_Al_slab_le3p2_nCl_le1", row, 0.0)

    near_decl = [row for row in rows if fval(row, "Al_slabMin_A") <= 4.0 and fval(row, "Al_nCl") <= 1.0]
    near_decl.sort(key=lambda r: (fval(r, "Al_slabMin_A"), fval(r, "Al_nCl")))
    for row in near_decl[:max_per_reason]:
        add_candidate(cands, label, "near_dechlorinated_Al_slab_le4p0_nCl_le1", row, 1.0)

    near = [row for row in rows if fval(row, "Al_slabMin_A") <= 5.0]
    near.sort(key=lambda r: fval(r, "Al_slabMin_A"))
    for row in near[:max_per_reason]:
        add_candidate(cands, label, "near_front_min_Al_slab_le5p0", row, 2.0)

    rows.sort(key=lambda r: fval(r, "Al_slabMin_A"))
    for row in rows[:max_per_reason]:
        add_candidate(cands, label, "per_run_min_Al_slab", row, 3.0)
    return cands


def seed_z_order(system: str) -> float:
    rows = read_csv(SEED_AUDIT_DIR / f"{system}_mgdep_start_texture.csv")
    if not rows:
        return math.nan
    return fval(rows[0], "z_order_0002")


def texture_candidates(label: str, system: str, max_per_reason: int) -> list[dict]:
    if "_r8mgdep_" not in label:
        return []
    rows = read_csv(TEXTURE_DIR / f"{label}_texture.csv")
    rows = [row for row in rows if math.isfinite(fval(row, "z_order_0002"))]
    if not rows:
        return []
    baseline = seed_z_order(system)
    rows.sort(key=lambda r: fval(r, "z_order_0002"))
    cands = []
    for row in rows[:max_per_reason]:
        frame = int(round(fval(row, "frame")))
        z = fval(row, "z_order_0002")
        cands.append(
            {
                "label": label,
                "reason": "texture_low_z_order_deposited_Mg",
                "md_step": frame * SAVE_STRIDE_STEPS,
                "t_ps": math.nan,
                "Al_slabMin_A": math.nan,
                "Al_height_A": math.nan,
                "Al_nCl": math.nan,
                "Al_nO": math.nan,
                "texture_frame_index": frame,
                "z_order_0002": z,
                "seed_z_order_0002": baseline,
                "delta_z_order_vs_seed": z - baseline if math.isfinite(baseline) else math.nan,
                "priority": 4.0,
            }
        )
    return cands


def dedupe(cands: list[dict], max_total: int) -> list[dict]:
    seen: set[tuple[str, int, str]] = set()
    out = []
    for cand in sorted(cands, key=lambda c: (float(c["priority"]), str(c["label"]), int(c["md_step"]))):
        key = (str(cand["label"]), int(cand["md_step"]), str(cand["reason"]))
        if key in seen:
            continue
        seen.add(key)
        out.append(cand)
        if len(out) >= max_total:
            break
    return out


def frame_atoms(cand: dict) -> object | None:
    traj = WORK / f"{cand['label']}_traj.xyz"
    if not traj.exists():
        cand["frame_status"] = "missing_traj"
        return None
    done_path = WORK / f"{cand['label']}_done.json"
    try:
        done = json.loads(done_path.read_text())
        n_frames = int(done.get("frames", 0))
        if n_frames <= 0:
            raise ValueError("done_json has no positive frame count")
        frame_idx = step_to_frame_index(int(cand["md_step"]), n_frames)
        at = read(traj, index=frame_idx)
    except Exception as exc:
        cand["frame_status"] = f"read_failed:{exc}"
        return None
    cand["frame_index"] = frame_idx
    cand["frame_status"] = "ok"
    parts = label_parts(str(cand["label"]))
    at.info["config_type"] = f"post_r8_{parts['system']}_{cand['reason']}"
    at.info["source_label"] = str(cand["label"])
    at.info["source_system"] = parts["system"]
    at.info["source_tag"] = parts["tag"]
    at.info["source_seed"] = parts["seed"]
    at.info["source_md_step"] = int(cand["md_step"])
    at.info["source_frame_index"] = frame_idx
    at.info["candidate_reason"] = str(cand["reason"])
    for key in [
        "t_ps",
        "Al_slabMin_A",
        "Al_height_A",
        "Al_nCl",
        "Al_nO",
        "z_order_0002",
        "seed_z_order_0002",
        "delta_z_order_vs_seed",
    ]:
        if key in cand and math.isfinite(float(cand[key])):
            at.info[key] = float(cand[key])
    return at


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def report(rows: list[dict], queue_path: Path) -> str:
    lines = [
        "# Post-r8 DFT/AIMD validation frame queue",
        "",
        "本报告只从带 `*_done.json` 的 post-r8 trajectories 中选帧；未完成或失败轨迹不会进入 DFT 队列。",
        "",
    ]
    if not rows:
        lines += [
            "## 当前状态",
            "",
            "尚无完成的 `r8neutral` / `r8mgdep` production run，因此没有可回流 CPU DFT/AIMD 的候选帧。",
            "",
        ]
    else:
        lines += [
            "## Selected frames",
            "",
            f"Queue: `{queue_path}`",
            "",
            "| label | step | frame | reason | Al-slab A | nCl | status |",
            "|---|---:|---:|---|---:|---:|---|",
        ]
        for row in rows:
            lines.append(
                f"| {row.get('label')} | {row.get('md_step')} | {row.get('frame_index', 'NA')} | "
                f"{row.get('reason')} | {row.get('Al_slabMin_A', 'NA')} | {row.get('Al_nCl', 'NA')} | "
                f"{row.get('frame_status', 'NA')} |"
            )
        lines.append("")
    lines += [
        "## Selection priority",
        "",
        "1. `Al_slabMin_A <= 3.2` and `Al_nCl <= 1`: strongest MLFF co-deposition geometry proxy.",
        "2. `Al_slabMin_A <= 4.0` and `Al_nCl <= 1`: near-contact/dechlorinated support frames.",
        "3. `Al_slabMin_A <= 5.0` and per-run minimum Al-slab distance: near-front coverage/active learning frames.",
        "4. `r8mgdep` low Mg(0002) z-order frames: texture-loss validation candidates.",
        "",
        "These frames are not final evidence until CPU DFT/AIMD validates forces/energetics and, where relevant, charge/coordination state.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    outdir = Path(argv[0]) if argv else OUTDIR
    max_per_reason = int(argv[1]) if len(argv) > 1 else 4
    max_total = int(argv[2]) if len(argv) > 2 else 64
    outdir.mkdir(parents=True, exist_ok=True)
    INCOMING.mkdir(parents=True, exist_ok=True)
    all_cands = []
    for label in completed_labels():
        parts = label_parts(label)
        all_cands.extend(cv_candidates(label, max_per_reason=max_per_reason))
        all_cands.extend(texture_candidates(label, parts["system"], max_per_reason=max_per_reason))
    selected = dedupe(all_cands, max_total=max_total)
    frames = []
    for cand in selected:
        at = frame_atoms(cand)
        if at is not None:
            frames.append(at)
    queue_path = INCOMING / "post_r8_dft_candidates.xyz"
    if frames:
        write(queue_path, frames)
    else:
        queue_path.write_text("", encoding="utf-8")
    write_csv(outdir / "selected_frames.csv", selected)
    (outdir / "selected_frames.json").write_text(json.dumps(selected, indent=2, default=str) + "\n", encoding="utf-8")
    (outdir / "REPORT_CN.md").write_text(report(selected, queue_path), encoding="utf-8")
    print(outdir / "REPORT_CN.md")
    print(f"completed_labels={len(completed_labels())} selected={len(selected)} written_frames={len(frames)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
