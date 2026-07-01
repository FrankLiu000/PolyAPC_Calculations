# T17 guarded MLFF-MD abort and active-learning queue

日期：2026-07-01  
体系：bare neutral MLFF-MD replicate  
label：`bare_neutral_seed2026070101_500ps`

## 结论

这条新 bare neutral seed **不能作为生产轨迹**。第一次未加 hard abort 的并跑在约 2-3.5 ps 出现大量 force-cap 事件和非物理温度/几何；加入 guard 后重跑，轨迹稳定越过 3.5 ps，但在 `step=8450` 触发第一个 force-cap 事件并自动停止。

```text
abort: 2026-07-01 08:09:10
step = 8450
t = 4.225 ps
reason = force-cap events=1
last written CV row before abort:
  step 8400, t=4.200 ps, T=659.1 K, Al_height=3.623 A, Al_slabMin=3.744 A, Al_nCl=2
```

按照发表级标准，任何 force-cap 事件都不能进入 production statistics；因此该 run 只作为模型外推 / active-learning 证据。

## 已采取的保护

`computational_v2/mlff/v3/interface_mlff_md.py` 已增加：

- `*_abort.txt`：记录 abort 原因；
- `*_done.json`：只有完整完成才写出；
- 温度、Al 几何、NaN force 和可选 force-cap abort；
- abort 时写出最后 trajectory，便于回标。

`run_neutral_replicates.sh` 已默认：

- `T17_ABORT_ON_CAP=1`；
- 只把 `*_done.json` 当作完成；
- 自动把 partial/failed `label_*` 移到 `failed/<label>_<timestamp>/` 后再重跑。

## Active-learning 队列

已抽取 abort 前后 9 帧用于 DFT 标注：

```text
computational_v2/mlff/incoming/t17_bare_seed2026070101_abort_unlabeled.xyz
frames = 9
source_md_step = 7000, 7200, 7400, 7600, 7800, 8000, 8200, 8400, 8450
source_time = 3.5-4.225 ps
file size = 168 KB
NUL = 0
```

这些帧的科学意义是：bare Al 阴离子可进入更近的 Mg 接触区，但现有 MLFF 在该 near-contact/cap 区域仍需要 DFT label 加固。它们不能证明 Al0 形成；下一步应在 CPU/DFT 节点对该队列做单点/短 AIMD 标注，检查 force error、qAl、Al-Cl 和 Al-Mg coordination，再决定是否加入下一轮 retrain。
