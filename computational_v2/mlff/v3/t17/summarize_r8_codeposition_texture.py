#!/usr/bin/env python3
"""Summarize gated post-r8 T17 MLFF-MD co-deposition and Mg texture probes.

The script is deliberately conservative: only runs with ``*_done.json`` are
treated as completed evidence. Missing trajectories, missing texture CSV files,
or failed/partial runs are reported as missing rather than inferred.
"""
from __future__ import annotations

import csv
import json
import math
import re
import sys
from pathlib import Path

import numpy as np


REPO = Path(__file__).resolve().parents[4]
WORK = REPO / "computational_v2" / "mlff" / "v3" / "t17"
TEXTURE_DIR = REPO / "results" / "T13_nucleation" / "mgdep_texture_r8"
SEED_AUDIT_DIR = REPO / "results" / "T13_nucleation" / "mgdep_seed_audit"
OUTDIR = REPO / "results" / "T17_reactive" / "post_r8_codeposition_texture_summary"
LABEL_RE = re.compile(r"^(bare|poly)_(r8neutral|r8mgdep)_seed(\d+)_([0-9.]+)ps$")


def finite_float(value: str | None) -> float:
    if value is None or value == "":
        return math.nan
    try:
        out = float(value)
    except ValueError:
        return math.nan
    return out if math.isfinite(out) else math.nan


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def tail_rows(rows: list[dict[str, str]], tail_frac: float) -> list[dict[str, str]]:
    if not rows:
        return []
    start = int(len(rows) * max(0.0, min(1.0, 1.0 - tail_frac)))
    return rows[start:]


def arr(rows: list[dict[str, str]], key: str) -> np.ndarray:
    return np.array([finite_float(row.get(key)) for row in rows], dtype=float)


def nanmean(values: np.ndarray) -> float:
    return float(np.nanmean(values)) if np.isfinite(values).any() else math.nan


def nanmin(values: np.ndarray) -> float:
    return float(np.nanmin(values)) if np.isfinite(values).any() else math.nan


def nanpercentile(values: np.ndarray, q: float) -> float:
    return float(np.nanpercentile(values, q)) if np.isfinite(values).any() else math.nan


def frac(mask: np.ndarray) -> float:
    if mask.size == 0:
        return math.nan
    valid = np.isfinite(mask.astype(float))
    if not valid.any():
        return math.nan
    return float(mask[valid].mean())


def label_parts(label: str) -> dict[str, str] | None:
    match = LABEL_RE.match(label)
    if not match:
        return None
    system, tag, seed, ps = match.groups()
    return {"system": system, "tag": tag, "seed": seed, "ps": ps}


def completed_labels() -> list[str]:
    labels = []
    for done in sorted(WORK.glob("*_done.json")):
        label = done.name[: -len("_done.json")]
        if LABEL_RE.match(label):
            labels.append(label)
    return labels


def cv_metrics(label: str, tail_frac: float) -> dict[str, object]:
    cv = WORK / f"{label}_cv.csv"
    all_rows = read_csv(cv)
    rows = tail_rows(all_rows, tail_frac)
    if not rows:
        return {
            "cv_status": "missing_or_empty",
            "n_cv_rows": len(all_rows),
            "n_tail_rows": 0,
        }
    slab = arr(rows, "Al_slabMin_A")
    height = arr(rows, "Al_height_A")
    ncl = arr(rows, "Al_nCl")
    temp = arr(rows, "T_K")
    tps = arr(all_rows, "t_ps")
    near32 = slab < 3.2
    near40 = slab < 4.0
    near50 = slab < 5.0
    near60 = slab < 6.0
    stripped = ncl <= 1.0
    return {
        "cv_status": "ok",
        "n_cv_rows": len(all_rows),
        "n_tail_rows": len(rows),
        "max_t_ps": nanmax(tps),
        "T_mean_K": nanmean(temp),
        "Al_slabMin_mean_A": nanmean(slab),
        "Al_slabMin_min_A": nanmin(slab),
        "Al_slabMin_p05_A": nanpercentile(slab, 5),
        "Al_slabMin_p50_A": nanpercentile(slab, 50),
        "Al_slabMin_p95_A": nanpercentile(slab, 95),
        "Al_height_mean_A": nanmean(height),
        "Al_nCl_mean": nanmean(ncl),
        "front_lt3p2_frac": frac(near32),
        "near_lt4p0_frac": frac(near40),
        "near_lt5p0_frac": frac(near50),
        "near_lt6p0_frac": frac(near60),
        "dechlorinated_frac": frac(stripped),
        "Al_codeposition_proxy_frac": frac(near32 & stripped),
        "near4_dechlorinated_frac": frac(near40 & stripped),
    }


def nanmax(values: np.ndarray) -> float:
    return float(np.nanmax(values)) if np.isfinite(values).any() else math.nan


def seed_baseline(system: str) -> dict[str, float]:
    path = SEED_AUDIT_DIR / f"{system}_mgdep_start_texture.csv"
    rows = read_csv(path)
    if not rows:
        return {}
    row = rows[0]
    return {
        "seed_z_order_0002": finite_float(row.get("z_order_0002")),
        "seed_I0002_over_I10m10": finite_float(row.get("texture_I0002_over_I10m10")),
    }


def texture_metrics(label: str, system: str, tail_frac: float) -> dict[str, object]:
    if "_r8mgdep_" not in label:
        return {"texture_status": "not_applicable"}
    tex = TEXTURE_DIR / f"{label}_texture.csv"
    all_rows = read_csv(tex)
    rows = tail_rows(all_rows, tail_frac)
    if not rows:
        return {
            "texture_status": "missing_or_empty",
            "n_texture_rows": len(all_rows),
            **seed_baseline(system),
        }
    nmg = arr(rows, "n_deposited_mg")
    zord = arr(rows, "z_order_0002")
    ratio = arr(rows, "texture_I0002_over_I10m10")
    base = seed_baseline(system)
    out = {
        "texture_status": "ok",
        "n_texture_rows": len(all_rows),
        "n_texture_tail_rows": len(rows),
        "deposited_mg_mean": nanmean(nmg),
        "deposited_mg_min": nanmin(nmg),
        "z_order_0002_mean": nanmean(zord),
        "I0002_over_I10m10_mean": nanmean(ratio),
        **base,
    }
    if "seed_z_order_0002" in base:
        out["delta_z_order_0002_vs_seed"] = out["z_order_0002_mean"] - base["seed_z_order_0002"]
    if "seed_I0002_over_I10m10" in base:
        out["delta_I0002_over_I10m10_vs_seed"] = out["I0002_over_I10m10_mean"] - base["seed_I0002_over_I10m10"]
    return out


def run_metrics(tail_frac: float) -> list[dict[str, object]]:
    rows = []
    for label in completed_labels():
        parts = label_parts(label)
        if parts is None:
            continue
        row: dict[str, object] = {"label": label, **parts}
        row.update(cv_metrics(label, tail_frac))
        row.update(texture_metrics(label, parts["system"], tail_frac))
        done_path = WORK / f"{label}_done.json"
        try:
            row["done_json"] = json.loads(done_path.read_text())
        except Exception:
            row["done_json"] = {}
        rows.append(row)
    return rows


def safe_div(num: float, den: float) -> float:
    if not math.isfinite(num) or not math.isfinite(den) or abs(den) < 1e-12:
        return math.nan
    return num / den


def pairwise(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_key: dict[tuple[str, str], dict[str, dict[str, object]]] = {}
    for row in rows:
        key = (str(row.get("tag")), str(row.get("seed")))
        by_key.setdefault(key, {})[str(row.get("system"))] = row
    out = []
    for (tag, seed), pair in sorted(by_key.items()):
        bare = pair.get("bare")
        poly = pair.get("poly")
        if bare is None or poly is None:
            out.append({"tag": tag, "seed": seed, "pair_status": "missing_bare_or_poly"})
            continue
        rec = {
            "tag": tag,
            "seed": seed,
            "pair_status": "ok",
            "bare_label": bare["label"],
            "poly_label": poly["label"],
        }
        for metric in [
            "Al_slabMin_mean_A",
            "Al_slabMin_min_A",
            "front_lt3p2_frac",
            "near_lt4p0_frac",
            "near_lt5p0_frac",
            "Al_codeposition_proxy_frac",
            "near4_dechlorinated_frac",
            "z_order_0002_mean",
            "I0002_over_I10m10_mean",
            "delta_z_order_0002_vs_seed",
            "delta_I0002_over_I10m10_vs_seed",
        ]:
            b = float(bare.get(metric, math.nan))
            p = float(poly.get(metric, math.nan))
            rec[f"{metric}_bare"] = b
            rec[f"{metric}_poly"] = p
            rec[f"{metric}_poly_minus_bare"] = p - b if math.isfinite(p) and math.isfinite(b) else math.nan
            rec[f"{metric}_poly_over_bare"] = safe_div(p, b)
        out.append(rec)
    return out


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys and key != "done_json":
                keys.append(key)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: object, digits: int = 3) -> str:
    try:
        val = float(value)
    except Exception:
        return "NA"
    return f"{val:.{digits}f}" if math.isfinite(val) else "NA"


def report_text(rows: list[dict[str, object]], pairs: list[dict[str, object]], tail_frac: float) -> str:
    lines = [
        "# Post-r8 T17 co-deposition / Mg texture summary",
        "",
        "本报告只汇总带有 `*_done.json` 的 post-r8 轨迹；缺失、失败或部分轨迹不会被当作证据。",
        f"tail fraction: {tail_frac}",
        "",
    ]
    if not rows:
        lines += [
            "## 当前状态",
            "",
            "尚无完成的 `r8neutral` 或 `r8mgdep` production run。等待 r8 key-holdout gate 通过后再启动 gated runners。",
            "",
        ]
    else:
        lines += [
            "## Run-level metrics",
            "",
            "| label | Al-slab mean A | front<3.2 | codep proxy | texture status | z-order | I0002/I10-10 |",
            "|---|---:|---:|---:|---|---:|---:|",
        ]
        for row in rows:
            lines.append(
                f"| {row['label']} | {fmt(row.get('Al_slabMin_mean_A'))} | "
                f"{fmt(row.get('front_lt3p2_frac'))} | {fmt(row.get('Al_codeposition_proxy_frac'))} | "
                f"{row.get('texture_status', 'NA')} | {fmt(row.get('z_order_0002_mean'))} | "
                f"{fmt(row.get('I0002_over_I10m10_mean'))} |"
            )
        lines.append("")
    if pairs:
        lines += [
            "## Bare-vs-poly pairs",
            "",
            "| tag | seed | pair | codep poly/bare | near4-deCl poly-bare | texture delta poly-bare |",
            "|---|---|---|---:|---:|---:|",
        ]
        for row in pairs:
            lines.append(
                f"| {row.get('tag')} | {row.get('seed')} | {row.get('pair_status')} | "
                f"{fmt(row.get('Al_codeposition_proxy_frac_poly_over_bare'))} | "
                f"{fmt(row.get('near4_dechlorinated_frac_poly_minus_bare'))} | "
                f"{fmt(row.get('delta_z_order_0002_vs_seed_poly_minus_bare'))} |"
            )
        lines.append("")
    lines += [
        "## Interpretation guardrail",
        "",
        "- `Al_codeposition_proxy_frac = Al_slabMin_A < 3.2 A 且 Al_nCl <= 1`，是 MLFF-MD 中的还原/共沉积几何代理，仍需 DFT/AIMD holdout 佐证。",
        "- Mg(0002)织构指标只对 `r8mgdep` probe 有意义，且报告末段相对 seed baseline 的变化；初态本身不作为 poly 优势证据。",
        "- 若 bare 显示更高 codep proxy / near4-deCl，而 poly 保持更低 Al 接触并更好维持 Mg texture，才可作为 cryo-EM Mg(0002)差异的计算对应。",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    outdir = Path(argv[0]) if argv else OUTDIR
    tail_frac = float(argv[1]) if len(argv) > 1 else 0.5
    outdir.mkdir(parents=True, exist_ok=True)
    rows = run_metrics(tail_frac)
    pairs = pairwise(rows)
    write_csv(outdir / "run_metrics.csv", rows)
    write_csv(outdir / "pairwise_comparison.csv", pairs)
    (outdir / "run_metrics.json").write_text(json.dumps(rows, indent=2, default=str) + "\n", encoding="utf-8")
    (outdir / "pairwise_comparison.json").write_text(json.dumps(pairs, indent=2, default=str) + "\n", encoding="utf-8")
    (outdir / "REPORT_CN.md").write_text(report_text(rows, pairs, tail_frac), encoding="utf-8")
    print(outdir / "REPORT_CN.md")
    print(f"completed_runs={len(rows)} pair_rows={len(pairs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
