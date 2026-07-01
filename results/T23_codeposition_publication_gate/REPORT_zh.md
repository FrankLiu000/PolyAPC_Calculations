# Mg/Al 共沉积证据发表级门槛审计（AIMD + MLFF-MD + classical-MD）

日期：2026-07-01  
目标：完成发表级 AIMD、MLFF-MD 和 classical-MD，找到并验证 Mg/Al 共沉积证据。

## 2026-07-01 07:46 CST 恢复更新

本机死机后已按 OOM-safe 策略恢复 GPU 节点计算，并将 CUDA 使用率提升到接近满载但仍保留显存/内存安全余量。

当前并行运行：

```text
REUS: PID 1589, out_dir = computational_v2/mlff/umb_poly_reus_dt05
      dt = 0.5 fs, force cap = 60 eV/A, sanity abort = |CV| > 25 A or fmax > 200 eV/A
T17:  PID 2435, bare_neutral_seed2026070101_500ps
      500 ps target, dt = 0.5 fs, ForceCap60, seed = 2026070101
GPU:  utilization ~94 %, memory 5.5 / 16.4 GB, free ~10.6 GB
WSL:  MemAvailable ~26 GB, swap = 0
```

关键恢复判断：

- 旧 `umb_poly_reus` 目录在 `z0=5.0` 恢复时产生过非物理坏行：`CV ~ 4.8e5-1.0e6 A`、`fmax ~ 1.6e6-1.0e7 eV/A`。该目录保留为失败审计，不作为正式 PMF 输入。
- 已在 `reus.py` 中加入 `ForceCap`、`REUS_DT_FS`、`REUS_MAX_ABS_CV`、`REUS_MAX_FMAX` 和 `reus_abort.txt` 保护；`run_poly_reus.sh` 默认使用 `REUS_DT_FS=0.5` 并输出到干净目录 `umb_poly_reus_dt05`。
- 100 fs 单窗口探针 `umb_poly_reus_probe_z50_dt05_20260701_0737` 通过：`cap=0, nan=0`，`fmax ~3-4 eV/A`。
- 正式 `umb_poly_reus_dt05` 已跨过此前最不稳定的 `z0=5.0` 窗口：`500 fs` 末行 `CV=5.2813 A, mgO=1, mgCl=2, Mg-Mg=6.610 A, fmax=3.691 eV/A`，无 abort。

当前 ETA 粗估：

- REUS 第一 cycle 约 30 min 量级，50 cycles 约 25-27 h；与 T17 并跑时以实际 `reus_state.txt` 推进重新估算。
- T17 neutral 500 ps 单条在当前并跑速度约 20-23 h；`run_neutral_replicates.sh` 会顺序补 bare/poly、两个 seed，目标是把 MLFF support 从 500 ps x1 推向独立种子复现。

这些计算只补强 **poly 降低 Al 阴离子进入 productive contact / desolvation pathway 的统计证据**。它们不能替代 T23 AIMD publication gate；AIMD 仍需达到 bare 3 seeds x 3 ps sustained contact + low qAl，以及 matched poly negative controls。

### 07:52 CST 纠正：T17 并跑尝试作废

`bare_neutral_seed2026070101_500ps` 在约 2-3.5 ps 出现大量 force-cap 事件和非物理温度/几何：

```text
2 ps log: cap = 1238
3.2-3.5 ps: T ~1.8-2.6e6 K, Al_height < -40 A to -22 A, Al_slabMin ~99-114 A
```

该 T17 run 已停止，partial `*_cv.csv` 只作为失败审计，不能进入 MLFF 生产统计。`interface_mlff_md.py` 已加入温度、几何、NaN 和可选 force-cap abort；`run_neutral_replicates.sh` 默认 `T17_ABORT_ON_CAP=1`，并只把 `*_done.json` 作为完成标志。当前 GPU 仅保留 `umb_poly_reus_dt05` 稳定推进；后续 T17 需要先短探针通过 cap=0 / no-abort 后再恢复 500 ps 生产。

08:09 CST guarded 重启的结果：同一 seed/start 的 2.5 ps probe 通过 `cap=0,nan=0`，但 500 ps 生产重启在 `step=8450`（4.225 ps）触发第一个 force-cap 事件后按设计 abort。已抽取 9 个 abort 前后帧到：

```text
computational_v2/mlff/incoming/t17_bare_seed2026070101_abort_unlabeled.xyz
source_time = 3.5-4.225 ps
purpose = DFT labelling / active-learning retrain
```

因此当前 MLFF replicate 结论是 **新 bare seed 暴露出 near-contact 外推缺口**，不是新增 500 ps 生产统计。REUS 仍是当前唯一长时 GPU production。

## 2026-07-01 08:28 CST T23 live update

远端 CPU 节点 `/home/ls/PolyAPC_DFT_work/hpc/t23` 的 live monitor 已归档到：

```text
results/T23_codeposition_publication_gate/live_20260701_0828/
```

当前判断：

- `publication_ready = false`
- strict interim 0.5 ps event 仍未通过；
- near-contact 0.5 ps event 已通过，且已有 2 个 bare seeds 支持；
- near-contact + `nCl<=1` 支持已通过 1 个 seed，第二个 seed 正接近 0.5 ps；
- 两个运行中的 T23b bare contact-release jobs 数值健康：fatal/warning = 0。

关键数值：

| seed | last geom fs | Al-slab / A | qAl Mulliken | strict longest/current fs | near longest/current fs | near+nCl<=1 longest/current fs | MgCoord longest/current fs | verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| bare s1 300 K | 1785 | 2.784 | 0.1817 | 240 / 55 | 915 / 320 | 740 / 320 | 1785 / 1785 | promising early slab-contact+low-qAl; continue |
| bare s2 325 K | 845 | 2.829 | 0.2107 | 200 / 0 | 720 / 720 | 475 / 475 | 720 / 720 | near-contact low-qAl with nCl<=1; continue |

这比 07:24 的 support-level evidence 更强：s1 已接近 1.8 ps release，MgCoord low-qAl 全程连续；s2 的 near-contact low-qAl 当前连续 720 fs，near+nCl<=1 当前连续 475 fs，离 0.5 ps supporting diagnostic 只差约 25 fs。**但 strict slab-contact longest 仍只有 240/200 fs，所以不能写成 strict AIMD interim，更不能写成 publication-ready spontaneous Al plating。**

## 2026-07-01 08:34 CST REUS dt05 progress

WSL GPU REUS 进度摘要已归档：

```text
results/T17_reactive/reus_dt05_progress_20260701_0834.{md,csv,json}
```

状态：

```text
out_dir = computational_v2/mlff/umb_poly_reus_dt05
state = 1000 fs
completed cycles = 2 / 50
windows >= state = 28 / 28
exchange acceptance = 9/27 = 33%
cap/nan = 7 / 0
GPU memory ~3.8 GB / 16.4 GB; WSL swap = 0
```

健康判断：第二个 cycle 后所有窗口都至少覆盖到 1000 fs；写出的自由区 fmax 分布总体正常，绝大多数窗口最大 fmax 为 3-6 eV/A，只有 `z0=7.0 A` 出现 1 个 `fmax=30.9 eV/A` 点，未出现 `fmax>40` 或 NaN。`cap=7` 说明仍有少量 raw force spike 或固定区/外推事件，最终 PMF 必须报告该 caveat；当前只可作为 live progress / health evidence，不是 PMF 收敛结论。

## 结论先行

目前证据链已经足以支撑一个谨慎机制：**APC Al 阴离子不是在远离金属表面时自发还原，而是在进入 Mg 内层接触区后发生 contact-gated electron transfer，随后形成 metallic / alloy-like Al-Mg 电子态；poly-APC 通过降低 cathode 还原前沿的 Al 阴离子接触机会并保持 Si/O-rich、Al-poor 接触层，降低这一路径概率。**

但还没有达到“发表级直接 AIMD 观察到 bare spontaneous Al plating”的门槛。当前直接 AIMD 证据是 **contact-gated / pre-contact-prepared**，不是自由长轨迹自发事件。T23 正在补这个短板。

## 发表级证据门槛

### AIMD / DFT

最低可发表标准：

- bare 至少 3 个 velocity seeds，每个 release 轨迹 3 ps。
- 每个 seed 需要维持 Al-slab productive contact + low qAl 的持续窗口，而不是单帧接触。
- 0.5 ps 是 interim event 门；3 ps x 3 是 publication gate。
- poly 需要 matched negative controls：同等 charge/温度/时间窗内不出现 sustained Al-slab contact + low qAl。
- 必须报告 qAl、Al-slab distance、Al-Cl bond weakening / nCl、Al-Mg coordination，并区分 Mulliken/Hirshfeld 的适用边界。

### MLFF-MD

最低可发表标准：

- neutral standoff / interface access：bare + poly 至少 200 ps x 3 independent seeds；推荐 500 ps x 3。
- biased q=-2 / cathodic drive：bare + poly 至少 200 ps x 3；推荐 500 ps x 3。
- 必须存档原始 `*_traj.xyz`、`*_cv.csv`、模型 hash、start hash、seed、force cap、NaN/cap counters。
- 每个 MLFF 结论必须有 DFT held-out force/energy MAE；near-contact 或 high-uncertainty frames 要回到 DFT/AIMD spot-check。
- MLFF-MD 不能单独证明 Al0 形成；它负责给出 Al-anion access/standoff、desolvation gate 和 DFT/AIMD 需要标注的 near-contact frames。

### classical-MD

最低可发表标准：

- bare vs poly 平行报告。
- field / eq 轨迹长度足够，face 定义经 reference slab 修正。
- 只用于 solvent-structure / contact-opportunity，不用于电子转移、Al0 或 Mg-Al alloy 直接判断。
- 不声称 transport advantage。

## 当前证据矩阵

| 证据块 | 当前状态 | 支撑力度 | 可写什么 | 不能写什么 |
|---|---|---|---|---|
| C1/T2-T4 DFT thermodynamics | 已完成 | 强 | Al 阴离子还原后 Al-Cl scission 和 Mg-Al 捕获/合金化热力学有利 | 不能证明动态自发发生 |
| C1_TS mechanism | 已完成 | 强 | bare 反应坐标可连通；入口被 poly standoff/passivation 抑制 | 不是长时动力学统计 |
| T10 unbiased / field AIMD | 已完成负结果 | 中-强 | 短时无偏 AIMD 不显示自发 Al plating，事件是 rare / activated | 不能声称已在自由 AIMD 看到 spontaneous plating |
| T10b steered contact AIMD | 已完成 | 强机制证据 | Al-Mg 距离进入约 2.6 A 后 qAl 从约 0.45 降到约 0.23；Al-Cl 同步弱化；ET-first/contact-gated | 不能称为 spontaneous；release 太短且回退 |
| T23 contact-frame release | 进行中 | 支持性证据增强，但 strict/publication gate 未过 | 23:00 ETA 记录：s1 到 1120 fs，MgCoord low-qAl 连续 1120 fs；near/near+deCl support 已过 0.5 ps；s2 到 510 fs，near/MgCoord 当前 385 fs | strict slab-contact 0.5 ps 尚未出现；不能称 spontaneous/publication-ready |
| T17 neutral MLFF-MD | 长轨迹已找回并审计 | 强支持性，但不是直接 Al0 证据 | matched 500 ps x1：bare Al_slabMin 4.58 ± 0.19 A，poly 7.57 ± 0.79 A；poly q=-2 1 ns 仍为 8.46 ± 0.32 A | 不能单独证明 Al0/Mg-Al；仍未达到 200/500 ps x3 independent seeds |
| REUS / MLFF PMF | 已恢复运行 | 正在补 desolvation/access 门控 | 可望提供 poly approach/desolvation gate 的更强统计 | 不是 Al0 形成证据 |
| T5 classical-MD v3.6 | 已修正并提交 | 对接触机会有利 | cathode/faceB 侧 ANI atom density：bare 1.906 vs poly 0.574 /nm2；poly 降低还原前沿 anion 接触机会 | 不能证明 Al0/Mg-Al；total near-surface ANI 未降低 |

## 当前 T23 门槛状态

依据本地镜像 2026-06-30 23:00 CST ETA 记录
`_external/PolyAPC_DFT_work_mirror/results/T23_md_length_audit/T23_ETA_STATUS_20260630_2300.md`：

- `publication_ready = false`
- bare contact release 总 seed = 3，已启动 = 2
- strict interim 0.5 ps event = false
- near-contact interim 0.5 ps event = true
- near+dechlorinated 0.5 ps support = true
- bare publication replicates = false
- poly publication negative controls = false

关键 23:00 状态：

```text
t23b_codep_contact_release_bare_qm2_s1_300K
  trajectory = 1120 fs
  last Al-slab = 2.917 A
  last qAl(Mulliken) = 0.102
  strict slab-contact low-qAl longest/current = 240/0 fs
  near_slab_contact_low_qAl longest/current = 915/20 fs
  near + nCl<=1 longest/current = 740/20 fs
  MgCoord low-qAl longest/current = 1120/1120 fs

t23b_codep_contact_release_bare_qm2_s2_325K
  trajectory = 510 fs
  last Al-slab = 2.809 A
  last qAl(Mulliken) = 0.124
  strict slab-contact low-qAl longest/current = 200/0 fs
  near_slab_contact_low_qAl longest/current = 385/385 fs
  near + nCl<=1 longest/current = 150/140 fs
  MgCoord low-qAl longest/current = 385/385 fs

t23b_codep_contact_release_bare_qm2_s3_350K
  pending / no frames in 23:00 audit
```

判断：T23 已经从“早期接触”推进到 **support-level 0.5-1.0 ps evidence**：s1 低 qAl + MgCoord 连续 1.12 ps，且 near/near+deCl 曾连续超过 0.5 ps；s2 也接近 0.5 ps near/MgCoord support。但 **strict slab-contact** 窗口碎片化，最长仍只有 240 fs/200 fs，当前为 0，因此不能写成 strict interim，更不能写 publication-ready spontaneous plating。

下一次合理检查点：2026-07-01 02:30 CST，重点看 s2 near/MgCoord 是否过 500 fs、s1/s2 strict slab-contact 是否重新形成连续窗口；检查前不要短间隔刷新。

## 当前 MLFF-MD / REUS 状态

### T17 source-verified audit 更新（2026-07-01）

WSL 原始目录 `computational_v2/mlff/v3/t17/` 中已经找回并审计 T17 长轨迹，输出见：

```text
results/T17_reactive/audit_t17_mlff.py
results/T17_reactive/mlff_production_audit.csv
results/T17_reactive/mlff_production_audit.json
results/T17_reactive/REPORT.md
```

关键数值：

```text
neutral matched 500 ps x1:
  bare Al_slabMin = 4.58 ± 0.19 A, Al_slabMin < 5 A = 98.9%
  poly Al_slabMin = 7.57 ± 0.79 A, Al_slabMin < 5 A = 0%

poly q=-2 1 ns negative control:
  Al_slabMin = 8.46 ± 0.32 A, Al_slabMin < 6 A = 0%, cap=0, nan=0
```

这修正了旧判断“当前 source-verified 只有 bare r2 23.65 ps 和 poly 50 ps”。现在 T17 可作为长时 MLFF-MD support 写入主线：poly 确实降低 Al 阴离子进入 Mg 电子转移前沿的概率。但它仍不能替代 AIMD 直接共沉积证据，也还未达到 200/500 ps x3 independent seeds 的最严格 MLFF 发表门槛。

GPU 上已恢复 poly REUS：

```text
目录：/lyz/Claude_workplace/PolyAPC_Calculations/computational_v2/mlff
脚本：run_poly_reus.sh
进程：python reus.py ... umb_poly_reus ...
恢复点：cycle 6, step 3000 fs；2026-07-01 00:24 CST 已确认跨过坏 checkpoint z=5.0/5.2 并继续推进
目标：50 cycles, 28 windows, z0 = 4.0-9.4 A
预计完成：需按 guarded run 重新估算；不要高频刷新
```

该计算对“poly 如何阻止 Al 阴离子进入 productive contact / desolvation pathway”有用，但仍需与 DFT/AIMD 的 qAl / Al-Cl / Al-Mg 证据闭环。

## 目前最短板

1. **AIMD publication gate 未过。** T23 需要继续到至少 0.5 ps interim，并最终 3 ps x 3 bare seeds + matched poly negative controls。
2. **T17 MLFF-MD 已补强但 replicates 不足。** 当前已有 matched 500 ps x1 + poly q=-2 1 ns 负控，足以支撑 access/standoff 机制；但还不足以宣称 MLFF production 达到 200/500 ps x3 independent seeds。
3. **classical-MD 已可用于结构分布，但不证明还原。** v3.6 cathode 指标对 poly 有利，但必须作为 contact-opportunity 证据，而不是 Al0 证据。

## 下一步执行顺序

1. 在 ETA 附近检查 T23：若 s1 达到 >=0.5 ps near_slab_contact_low_qAl，并且 qAl 维持低值，立即归档 interim milestone；若失败，启动 T23c/T23d weak-hold-and-release。
2. 等 poly REUS 完成后运行 WHAM，生成 PMF / convergence drift / bootstrap error；若未完成，估算新 ETA。
3. 视主稿风险决定是否继续补 T17 neutral/biased MLFF-MD replicates：目标至少 200 ps x3，推荐 500 ps x3；现有 `*_cv.csv` 已 source-verified，优先补 independent seeds 而不是重复同一 seed。
4. 对 classical-MD 的 cathode face 结果做 Al-center / molecule-whole PBC 复核，只把可靠指标纳入主稿。
