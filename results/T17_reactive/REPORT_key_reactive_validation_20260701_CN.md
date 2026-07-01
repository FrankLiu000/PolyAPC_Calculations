# T17 key-reactive MLFF validation and r8 holdout plan

Date: 2026-07-01 CST

## Why this check was needed

T17 的发表级目标不是一般的稳定 MD，而是要证明 bare-APC 更容易走向 APC Al 阴离子的近表面还原、脱氯和 Mg/Al 共沉积，而 poly-APC 抑制这一路径。此前 `r6_qcond` 可用于带电/偏压探索，但其实际训练集 `data_qcond/train.xyz` 不含 `al_bare_nearsurface`、`dep_bare_*` 或 `react_bare_clstrip_*` 帧。因此，直接用 `r6_qcond` 长跑 T17 容易把 force-cap/非物理事件误当作化学事件。

本轮只用 CPU 做 MACE 推断验证，不与正在运行的 poly REUS 抢 GPU。

## Data inspected

- `computational_v2/mlff/incoming/al_queue_bare_t17_labeled.xyz`
  - 8 frames, 172 atoms, `config_type=al_bare_nearsurface`
  - real DFT energies/forces; nonzero-force frames = 8/8
- `computational_v2/mlff/incoming/reactive_kpoint_deposition_set.xyz`
  - 18 frames, 65/172 atoms
  - Al-on-Mg deposition frames: `dep_bare_*`, gamma/k-point mixed according to bonded-regime convergence
  - Cl-strip frames: `react_bare_clstrip_*`

## Current-model validation

All values below are force MAE unless noted. These are not strict holdout results for `apc_v3_broad`, because the small key-reactive frames were present in the broad r6/r7 assembly; they are still useful as key-manifold consistency checks.

| model | evaluation set | result | verdict |
|---|---:|---:|---|
| `r6_qcond.model` | `reactive_kpoint_deposition_set.xyz` | global 83.5 meV/A; Cl-strip 103-135 meV/A | fail |
| `r6_qcond.model` | `al_queue_bare_t17_labeled.xyz` | 98.9 meV/A | fail |
| `apc_v3_broad.model` | `reactive_kpoint_deposition_set.xyz` | global 35.6 meV/A; deposition 1.8-6.2 meV/A; Cl-strip mostly 45-54 meV/A | pass as in-manifold check |
| `apc_v3_broad.model` | `al_queue_bare_t17_labeled.xyz` | 52.7 meV/A | borderline fail |

Outputs:

```text
results/T17_reactive/key_reactive_validation/
```

## Interpretation for the story

1. `apc_v3_broad` has learned the Al-on-Mg deposition geometry well enough to be a short-term candidate for neutral/proximity T17 probes.
2. `r6_qcond` has not seen the key co-deposition chemistry and should not be used as the publication model for bare spontaneous Al plating until retrained.
3. The failed/aborted T17 neutral run is consistent with a model-coverage problem near the Al-anion/Mg contact zone, not with reliable spontaneous Al plating evidence.
4. A publication-grade MLFF result now requires an explicit key-reactive holdout: Al near-surface, Al-on-Mg deposition, and Cl-strip must all be represented in test data.

## r8 holdout dataset prepared

Script:

```text
computational_v2/mlff/v3/assemble_key_reactive_holdout.py
```

Generated local split:

```text
computational_v2/mlff/v3/data_r8_keyholdout/
```

Summary:

```text
unique frames = 931
train / val / test_key = 790 / 69 / 72
al_bare_nearsurface = 5 train / 1 val / 2 test
dep_bare = 6 train / 1 val / 2 test
react_bare_clstrip = 5 train / 1 val / 2 test
```

The large `.xyz` split files are local derived products and can be regenerated from `incoming`; `split_report.csv/json` records the deterministic split.

## Next action

Do not launch more long T17 production while REUS is using the GPU. Once REUS reaches a checkpoint or a planned pause, run:

```bash
cd /lyz/Claude_workplace/PolyAPC_Calculations/computational_v2/mlff/v3
./train_r8_keyholdout.sh
```

The r8 gate is:

- key-holdout global force MAE <= 50 meV/A,
- no key group above ~75 meV/A without explanation,
- then rerun matched bare/poly T17 replicates with `run_neutral_replicates.sh`,
- any new Al-plating candidate frames must go back to CPU DFT validation before being used as evidence.
