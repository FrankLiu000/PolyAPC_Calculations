# T5 classical-MD / MLFF-MD 重分析中文报告（v3.6）

日期：2026-06-30 晚  
位置：`/lyz/Claude_workplace/PolyAPC_Calculations/results/T5_anion_interface/`

## 一句话结论

在经典 MD 层面，poly-APC 的优势不能写成“体相 Mg²⁺ 传输更快”，也不能单独写成“已经证明 Al 发生/不发生还原”；更稳健的表述是：POSS 网络改变 APC 离子对在 Mg 界面两侧的空间占据，使固定 faceB/cathode 的 `[Ph2AlCl2]-` 近表面原子密度显著低于 bare-APC，而真正的 Al 还原、Al0/Mg-Al 共沉积选择性仍需 AIMD/DFT 与反应性 MLFF 闭环。

## 已重新分析的数据

### 1. 经典 MD：200 ns eq + 200 ns field 已完成

数据来自 WSL：

- 工作区：`/lyz/Claude_workplace/polyAPC/storyT5/`
- 轨迹：`sym/bare_t21/field.part*.xtc` 与 `sym/poly_t21/field.part*.xtc`
- 参考结构：`sym/{bare_t21,poly_t21}/em3dc.gro`
- 分析脚本：`field_fixedface.py`、`field_anion_zones.py`、`fig_field_anion_z.py`

### 2. v3.5 结论被再次修正

v3.5 已经修正了 v3.4 的 RICH/POOR 标签翻转问题，但仍从 trajectory 第一帧推断 slab face。poly 轨迹中少数 wrapped Mg slab 原子导致 upper face 被误判到 z≈11.65 nm，而参考结构中的真实 upper inner Mg face 在 z≈17.55 nm。

我已把 `field_fixedface.py` 和 `field_anion_zones.py` 改为从 `em3dc.gro` 的两块 1794-atom Mg slab 直接确定 fixed faces，避免被 trajectory wrapping 干扰。

## v3.6 关键数字

使用 reference-face 后处理，0.6 nm 近表面壳层、discard 50 ns：

```text
bare-APC field 50-200 ns:
  ANI atoms faceA = 1.232 /nm2
  ANI atoms faceB = 1.906 /nm2
  total near       = 3.138 /nm2

poly-APC field 50-200 ns:
  ANI atoms faceA = 2.621 /nm2
  ANI atoms faceB = 0.574 /nm2
  total near       = 3.196 /nm2
```

tail window 130-200 ns：

```text
bare-APC:
  faceA = 1.181 /nm2
  faceB = 1.996 /nm2

poly-APC:
  faceA = 2.555 /nm2
  faceB = 0.538 /nm2
```

因此，若沿用此前的 faceB=cathode/plating-face 约定，poly 在 fixed faceB 上的 all-ANI-atom density 比 bare 低约 70%。但是 total near-surface ANI density 并没有降低，bare 为 3.138 /nm2，poly 为 3.196 /nm2。更准确的机制表述是“界面占据重分布”，不是“全界面 anion 总量减少”。

## 该结果如何进入主线

### 可用于主文的稳健点

1. **Transport 不是判据。** 既有 MD/GITT 结论仍然是 bulk transport null，不能声称 poly-APC 靠更快 Mg²⁺ 传输胜出。
2. **POSS 网络改变界面占据。** 经典 MD 支持 POSS 网络使 APC 离子对在 Mg 两侧界面重新分布；在 reference-face field 分析中，fixed faceB/cathode 的 `[Ph2AlCl2]-` 原子密度显著低于 bare。
3. **这是结构/动力学证据，不是还原证据。** 经典 OPLS/LJ wall 没有电子、image charge 或 Al0/Mg-Al 反应路径，只能回答 solvent-structure / contact-opportunity。

### 不能过度解释的点

1. all-ANI-atom density 不等于 Al metal centre 到达电子转移前沿。快速检查显示 Al-centre/COG 指标对阈值、取向和 PBC/molecule wrapping 很敏感，不能单独作为 Al plating 证据。
2. total near-surface anion 不再支持 v3.5 的 “poly 总近表面 anion -31%”。
3. classical field metric 不能替代 AIMD/DFT 的 redox selectivity，也不能直接说明是否形成 Al0 或 Mg-Al alloy。

## 已启动的 MLFF-MD 后续计算

GPU 环境可用：

- GPU：RTX 4070 Ti SUPER, 16 GB
- MLFF venv：`/lyz/Claude_workplace/polyAPC/.mlff_venv`
- 可用包：`torch 2.6.0+cu124`、`ase 3.28.0`、`mace 0.3.16`
- `chgnet/matgl/sevenn` 当前未装；现阶段不需要，因为已有 MACE 模型和 REUS 工作流。

已恢复 poly REUS：

```text
目录：/lyz/Claude_workplace/PolyAPC_Calculations/computational_v2/mlff
命令来源：run_poly_reus.sh
启动时间：2026-06-30 23:38 CST
进程：python reus.py ... umb_poly_reus ...
恢复点：cycle 6, step 3000 fs
目标：50 cycles, 28 windows, z0 = 4.0-9.4 Å
```

估计 ETA：2026-07-01 09:15-10:00 CST。线程 heartbeat 已更新到 2026-07-01 09:30 CST 检查一次，不再频繁刷新。

## 与 Mg/Al 共沉积证据的关系

经典 MD 与 MLFF-MD 当前支撑的是“反应前的界面接触机会/脱溶剂化门控”。真正发表级 Mg/Al 共沉积证据仍需满足以下任一强证据标准：

1. **bare-APC AIMD/DFT 直接证据：** Al-centre 接近 Mg slab，Al-Cl 断裂或显著弱化，Al Bader/拟合电荷降低，并出现 Al-Mg 配位或 Al0/Mg-Al alloy-like bonding。
2. **poly-APC 对照：** 相同偏压/温度/时间窗内不出现可分辨 Al0/Mg-Al 共沉积，且 Si/O-rich contact layer 保持 Al-poor。
3. **MLFF-MD/active learning：** 长时间、大体系采样给出 near-contact/desolvation gate 和高风险构型；这些构型必须回到 DFT/AIMD 标注验证，报告 force/energy MAE 或至少 near-surface DFT spot-check。

## 建议写法

> Classical MD shows that the POSS-derived network does not improve bulk ion transport, but reorganizes the interfacial occupancy of APC ion pairs. After correcting the face definition with reference Mg slabs, the field-biased poly-APC model exhibits markedly lower `[Ph2AlCl2]-` atomic density at the fixed cathodic face than bare-APC, while the total near-surface anion population remains similar. This result supports an interfacial access/solvent-structure contribution, not direct redox suppression. The latter is tested by AIMD/DFT and reactive MLFF through Al-Cl cleavage, Al charge reduction and Mg-Al coordination.

