#!/usr/bin/env bash
# mwfn_batch.sh <file.fchk|file.molden> ... — Multiwfn property batch (noGUI).
# Drives Multiwfn over stdin heredocs for each wavefunction file:
#   ESP V_S,min/max ; Fukui f+/dual descriptor ; spin density ; QTAIM (AIM) charges.
# Run on a wavefunction with the matching charge/multiplicity already in the .fchk.
set -euo pipefail

MWFN="${MWFN_BIN:-/CH/Multiwfn_3.8_dev_bin_Linux_noGUI/Multiwfn_noGUI}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-8}"
OUT="${OUT:-../../results/data}"   # relative to a phase gjf/ dir
mkdir -p "$OUT"

for wfn in "$@"; do
  base="$(basename "${wfn%.*}")"
  echo "[mwfn] $base"

  # --- ESP min/max on the molecular surface (quantitative analysis, opt 12) ---
  "$MWFN" "$wfn" > "$OUT/${base}_esp.txt" 2>&1 <<'EOF'
12
0
q
EOF

  # --- Fukui f+ / dual descriptor: needs this N, N+1, N-1 set; here single-file
  #     Hirshfeld charges + condensed Fukui via opt 7 sub-menu (fill on node where
  #     the +/- wavefunctions exist). Placeholder driver kept explicit. ---
  "$MWFN" "$wfn" > "$OUT/${base}_fukui.txt" 2>&1 <<'EOF'
7
18
1
0
q
EOF

  # --- Spin density (is the unpaired electron on Al?) — grid + atomic spin pop ---
  "$MWFN" "$wfn" > "$OUT/${base}_spin.txt" 2>&1 <<'EOF'
7
5
2
0
q
EOF

  # --- QTAIM / AIM atomic charges (basin integration) ---
  "$MWFN" "$wfn" > "$OUT/${base}_qtaim.txt" 2>&1 <<'EOF'
17
1
1
0
q
EOF
done
echo "[mwfn] done -> $OUT"
