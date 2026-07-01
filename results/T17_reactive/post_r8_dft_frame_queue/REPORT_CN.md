# Post-r8 DFT/AIMD validation frame queue

本报告只从带 `*_done.json` 的 post-r8 trajectories 中选帧；未完成或失败轨迹不会进入 DFT 队列。

## 当前状态

尚无完成的 `r8neutral` / `r8mgdep` production run，因此没有可回流 CPU DFT/AIMD 的候选帧。

## Selection priority

1. `Al_slabMin_A <= 3.2` and `Al_nCl <= 1`: strongest MLFF co-deposition geometry proxy.
2. `Al_slabMin_A <= 4.0` and `Al_nCl <= 1`: near-contact/dechlorinated support frames.
3. `Al_slabMin_A <= 5.0` and per-run minimum Al-slab distance: near-front coverage/active learning frames.
4. `r8mgdep` low Mg(0002) z-order frames: texture-loss validation candidates.

## CPU labeling handoff

After this queue is non-empty on the CPU node, run:

```bash
cd /CH/Claude_Calcs_20260603/computational_v2/mlff/incoming
sbatch submit_post_r8_label.sbatch
```

`split_post_r8_label_batches.py` will split mixed bare/poly/mgdep frames by Natoms, charge, and cell before calling `label_forces.py`.

These frames are not final evidence until CPU DFT/AIMD validates forces/energetics and, where relevant, charge/coordination state.
