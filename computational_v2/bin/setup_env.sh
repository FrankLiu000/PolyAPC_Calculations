#!/usr/bin/env bash
# setup_env.sh — build the user-space Python env for structure/input generation
# and figure/parser scripts. RUN ON THE LOGIN NODE ONLY (never under sbatch).
#
# This does NOT install Gaussian/CP2K/Multiwfn/ORCA — those are the
# site-installed binaries referenced by run_g16.sh / run_cp2k.sh / mwfn_batch.sh.
set -euo pipefail

PREFIX="${MINICONDA_PREFIX:-$HOME/miniconda3}"
ENV_NAME="${ENV_NAME:-build}"

if ! command -v conda >/dev/null 2>&1 && [ ! -x "$PREFIX/bin/conda" ]; then
  echo "[setup_env] installing Miniconda into $PREFIX"
  tmp=$(mktemp -d)
  curl -fsSL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o "$tmp/mc.sh"
  bash "$tmp/mc.sh" -b -p "$PREFIX"
  rm -rf "$tmp"
fi
# shellcheck disable=SC1091
source "$PREFIX/etc/profile.d/conda.sh"

if ! conda env list | grep -q "^$ENV_NAME "; then
  echo "[setup_env] creating conda env '$ENV_NAME'"
  conda create -y -n "$ENV_NAME" python=3.11 ase pymatgen matplotlib numpy scipy rdkit pandas
fi

conda activate "$ENV_NAME"
python -c "import ase, pymatgen, rdkit, numpy, scipy, matplotlib, pandas; print('[setup_env] python build env OK')"
echo "[setup_env] done. 'conda activate $ENV_NAME' before running the generators."
