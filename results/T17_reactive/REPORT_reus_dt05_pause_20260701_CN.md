# Poly REUS dt05 pause note

Date: 2026-07-01 CST

## What happened

`umb_poly_reus_dt05` was restarted after the local crash with conservative settings:

```text
dt = 0.5 fs
ForceCap = 60 eV/A
28 windows, z0 = 4.0-9.4 A
tau = 500 fs
```

It reached 1000 fs/window cleanly enough for a live health note. By cycle 3 it reached 1500 fs/window, but ForceCap events jumped sharply:

```text
cycle 1, 500 fs:  cap=0, nan=0
cycle 2, 1000 fs: cap=7, nan=0
cycle 3, 1500 fs: cap=1991, nan=0
```

Window diagnostics at 1500 fs show that the problem is concentrated:

```text
z0=5.2 A: fmax_max=61.869 eV/A, p95=60.066, n_fmax_gt40=25
z0=6.4 A: fmax_max=60.003 eV/A, p95=60.000, n_fmax_gt40=25
z0=7.0 A: one fmax=30.917 eV/A point
other windows: mostly fmax_max ~3-9 eV/A
```

The REUS process was terminated intentionally after cycle 3. This was a data-quality pause, not an OOM/GPU failure.

## Consequence

The current `umb_poly_reus_dt05` data are retained as an audit trail and early health/progress evidence, but they are **not** a publication-grade PMF and should not be plotted as a converged free-energy profile.

The safe next step is not to continue the same REUS blindly. We should first improve the MLFF coverage around the problematic contact/CV region, which is now being addressed by `t16_broad_r8_keyholdout` training.

## Restart gate

Restart REUS only after:

- r8 key-holdout validation passes or the problematic windows are DFT-checked,
- a short 5.0-6.6 A window-only REUS/umbrella smoke run has cap=0 or a clearly explained low cap count,
- PMF production is restarted from a clean output directory with the pause caveat documented.
