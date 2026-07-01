#!/usr/bin/env python3
"""Gate r8 key-holdout validation before allowing T17 production.

Usage:
    gate_key_holdout.py <metrics.csv> [out.json]
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


KEY_GROUPS = {
    "al_bare_nearsurface": ("al_bare_nearsurface",),
    "dep_bare": ("dep_bare",),
    "react_bare_clstrip": ("react_bare_clstrip",),
}
GLOBAL_MAX = 50.0
KEY_GROUP_MAX = 75.0


def weighted(rows: list[dict[str, str]]) -> float | None:
    num = den = 0.0
    for row in rows:
        n = float(row["n"])
        num += n * float(row["force_mae_mev_A"])
        den += n
    return num / den if den else None


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    metrics = Path(argv[0])
    out = Path(argv[1]) if len(argv) > 1 else metrics.with_name(metrics.stem.replace("_metrics", "") + "_gate.json")
    rows = list(csv.DictReader(metrics.open()))
    global_rows = [row for row in rows if row["config_type"] == "GLOBAL"]
    global_mae = float(global_rows[0]["force_mae_mev_A"]) if global_rows else weighted(rows)
    groups = {}
    failures = []
    if global_mae is None or global_mae > GLOBAL_MAX:
        failures.append(f"GLOBAL force MAE {global_mae} > {GLOBAL_MAX} meV/A")
    for name, prefixes in KEY_GROUPS.items():
        subset = [
            row for row in rows
            if row["config_type"] != "GLOBAL" and any(row["config_type"].startswith(prefix) for prefix in prefixes)
        ]
        mae = weighted(subset)
        groups[name] = {
            "n_rows": len(subset),
            "n_frames": int(sum(float(row["n"]) for row in subset)),
            "force_mae_mev_A": mae,
        }
        if not subset:
            failures.append(f"{name} missing from key holdout metrics")
        elif mae is not None and mae > KEY_GROUP_MAX:
            failures.append(f"{name} force MAE {mae:.1f} > {KEY_GROUP_MAX} meV/A")
    payload = {
        "metrics": str(metrics),
        "thresholds": {"global_force_mae_mev_A": GLOBAL_MAX, "key_group_force_mae_mev_A": KEY_GROUP_MAX},
        "global_force_mae_mev_A": global_mae,
        "key_groups": groups,
        "passed": not failures,
        "failures": failures,
    }
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
