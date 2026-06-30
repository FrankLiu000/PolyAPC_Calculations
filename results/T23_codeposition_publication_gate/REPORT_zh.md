# Mg/Al 共沉积证据发表级门槛审计（AIMD + MLFF-MD + classical-MD）

日期：2026-06-30  
目标：完成发表级 AIMD、MLFF-MD 和 classical-MD，找到并验证 Mg/Al 共沉积证据。

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
| T23 contact-frame release | 进行中 | 当前为支持性早期证据 | s1 已到 320 fs，near_slab_contact_low_qAl 连续 320 fs，MgCoord low-qAl 连续 320 fs；s2 已启动 50 fs | 未过 0.5 ps interim，更未过 3 ps x 3 publication gate |
| T17 neutral MLFF-MD | 长轨迹已找回并审计 | 强支持性，但不是直接 Al0 证据 | matched 500 ps x1：bare Al_slabMin 4.58 ± 0.19 A，poly 7.57 ± 0.79 A；poly q=-2 1 ns 仍为 8.46 ± 0.32 A | 不能单独证明 Al0/Mg-Al；仍未达到 200/500 ps x3 independent seeds |
| REUS / MLFF PMF | 已恢复运行 | 正在补 desolvation/access 门控 | 可望提供 poly approach/desolvation gate 的更强统计 | 不是 Al0 形成证据 |
| T5 classical-MD v3.6 | 已修正并提交 | 对接触机会有利 | cathode/faceB 侧 ANI atom density：bare 1.906 vs poly 0.574 /nm2；poly 降低还原前沿 anion 接触机会 | 不能证明 Al0/Mg-Al；total near-surface ANI 未降低 |

## 当前 T23 门槛状态

依据本地 `results/T23_md_length_audit/t23_publication_gate.json`：

- `publication_ready = false`
- bare contact release 总 seed = 3，已启动 = 2
- interim 0.5 ps event = false
- bare publication replicates = false
- poly publication negative controls = false

关键早期里程碑：

```text
t23b_codep_contact_release_bare_qm2_s1_300K
  last_time_fs = 320 fs
  last Al-slab = 2.683 A
  last qAl(Mulliken) = 0.221
  near_slab_contact_low_qAl longest/current = 320/320 fs
  MgCoord low-qAl longest/current = 320/320 fs
  strict slab-contact low-qAl longest/current = 85/65 fs
  near + nCl<=1 longest/current = 145/145 fs

t23b_codep_contact_release_bare_qm2_s2_325K
  last_time_fs = 50 fs
  last Al-slab = 2.655 A
  last qAl(Mulliken) = 0.256
  near_slab_contact_low_qAl longest/current = 50/50 fs

t23b_codep_contact_release_bare_qm2_s3_350K
  not started / no frames in current audit
```

判断：T23 已经超过旧 `/CH` 48 fs release 的长度，但还未过 0.5 ps interim gate。下一次应在 ETA 附近检查，不要短间隔刷新。

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
