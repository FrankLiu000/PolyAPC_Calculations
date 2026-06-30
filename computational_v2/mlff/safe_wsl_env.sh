#!/usr/bin/env bash
# Conservative defaults for local WSL compute jobs.
#
# Source this file before GPU/MD post-processing tasks to keep CPU thread
# fan-out and memory use predictable on the shared Windows workstation.

export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-1}"
export VECLIB_MAXIMUM_THREADS="${VECLIB_MAXIMUM_THREADS:-1}"
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True,max_split_size_mb:128}"

require_mem_gb() {
  local min_gb="${1:-8}"
  local avail_kb
  avail_kb="$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)"
  local avail_gb=$((avail_kb / 1024 / 1024))
  if [ "$avail_gb" -lt "$min_gb" ]; then
    echo "Refusing to start: WSL MemAvailable=${avail_gb}GiB < required ${min_gb}GiB" >&2
    return 2
  fi
}

require_vram_free_gb() {
  local min_gb="${1:-4}"
  if ! command -v nvidia-smi >/dev/null 2>&1; then
    echo "Refusing to start: nvidia-smi is not available" >&2
    return 2
  fi
  local free_mib
  free_mib="$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -n 1 | tr -d ' ')"
  local free_gb=$((free_mib / 1024))
  if [ "$free_gb" -lt "$min_gb" ]; then
    echo "Refusing to start: CUDA memory free=${free_gb}GiB < required ${min_gb}GiB" >&2
    return 2
  fi
}

ensure_no_process() {
  local pattern="$1"
  local message="$2"
  if pgrep -af "$pattern" >/dev/null; then
    echo "$message" >&2
    pgrep -af "$pattern" >&2 || true
    return 2
  fi
}
