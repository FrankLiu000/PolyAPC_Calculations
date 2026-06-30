# T17 — reactive interface MLFF-MD source-verified audit

日期：2026-07-01  
节点：GPU / WSL LYZ-ROG  
原始数据：`computational_v2/mlff/v3/t17/`  
审计脚本：`results/T17_reactive/audit_t17_mlff.py`  
机器可读输出：`mlff_production_audit.csv`, `mlff_production_audit.json`

## 结论

此前 T23 gate 报告中“T17 source-verified 只有 bare r2 23.65 ps 和 poly 50 ps”的判断已经过期。WSL 原始目录中实际存在并已审计的 matched neutral MLFF-MD 长轨迹为：

- **bare neutral:** `bare_final_s1_cv.csv` + `bare_final_cv.csv`，总长约 **500 ps**。
- **poly neutral:** `poly_r6_s1_cv.csv` + `poly_r6_cv.csv`，总长约 **500 ps**。
- 每段丢弃前 50 ps 后，bare/poly 各保留 **400 ps production**，采样间隔 0.025 ps。

主结果是：**poly-APC 把可还原 Al 阴离子从 Mg 电极 3D 接触前沿显著推远**。这支持“界面组成/氧化还原选择性优势”，但不是直接 Al0 生成证据。

## Primary Neutral Matched MLFF-MD

| 指标，t > 50 ps / segment | bare | poly |
|---|---:|---:|
| 总 production 采样点 | 16000 | 16000 |
| Al_slabMin 平均值 | **4.58 ± 0.19 Å** | **7.57 ± 0.79 Å** |
| Al_slabMin 中位数 | 4.58 Å | 7.51 Å |
| Al_slabMin 5-95% | 4.26-4.88 Å | 6.30-8.84 Å |
| Al_slabMin 最小值 | 3.905 Å | 5.516 Å |
| Al_nCl 平均值 | 2.00 | 2.00 |
| Al_slabMin < 3.2 Å | 0% | 0% |
| Al_slabMin < 5.0 Å | **98.9%** | **0%** |
| Al_slabMin < 6.0 Å | 100% | 1.95% |

解释：

- **bare** 的 Al 阴离子几乎全程停在 5 Å 内，是“poised but unreduced”的 near-front 状态。
- **poly** 的 Al 阴离子最小距离也在 5.5 Å 以上，绝大多数时间维持 6-9 Å standoff。
- 两者的 Al-Cl 配位都保持 nCl = 2，因此这组 MLFF 轨迹本身不显示 Al-Cl 断裂或 Al0 生成。
- 因此 T17 的正确作用是证明 **access/contact probability**：poly 降低可还原 Al 阴离子进入 Mg 电子转移前沿的机会。

## Charged / Negative-Control Runs

| 轨迹 | 可靠性 | Al_slabMin production 结果 | 用途 |
|---|---|---:|---|
| `bare_qcond_cv.csv` | 100 ps，log: cap=0, nan=0 | 5.55 ± 0.17 Å | charge-conditioned 支持性参照 |
| `poly_qcond_cv.csv` | 100 ps，log: cap=0, nan=0 | 9.04 ± 0.41 Å | charge-conditioned poly standoff |
| `poly_qm2_1ns_cv.csv` | 1 ns，log: cap=0, nan=0 | 8.46 ± 0.32 Å | poly cathodic/q=-2 长时负控 |
| `bare_qm1_cv.csv` | **排除** | 42.7 ps 后 T > 10^6 K，force-cap > 7.4e4 | per-charge fine-tune 动力学失稳，不能作生产数据 |

`poly_qm2_1ns` 是当前最强的 poly 负控：在 1 ns cathodic/charged 条件下，Al_slabMin 仍为 8.46 ± 0.32 Å，`Al_slabMin < 6 Å` 为 0%，没有进入还原接触区。

## 发表级判断

T17 现在可以作为 **source-verified long MLFF-MD support** 写入主线，但边界如下：

- 可以写：poly-APC 在 matched atomistic Mg interface 中显著降低 Al 阴离子 near-front occupancy；bare 保持 near-front poised state；poly q=-2 1 ns 仍保持远离。
- 不能写：T17 直接观察到 Al0 或 Mg-Al 共沉积。MLFF 这里是 reactive-PES surrogate / access sampler，不是显式电子转移 AIMD。
- 仍未满足最严格的 MLFF publication target：neutral 和 biased 条件下 **200/500 ps x 3 independent seeds**。当前是 matched 500 ps x1 + poly q=-2 1 ns negative control。
- 直接共沉积证据仍必须来自 T23/AIMD：qAl 下降、Al-Cl 弱化、Al-Mg 配位、持续 release window。

## 与主故事的连接

T17 与 T5 classical-MD v3.6、T23/AIMD 的分工应这样写：

1. Classical-MD 证明 cathodic Mg face 附近的 ANI atom density 在 poly 中明显低于 bare，是 contact-opportunity 证据。
2. T17 MLFF-MD 进一步在 atomistic Mg interface 上证明可还原 **Al center** 的 3D electrode distance 从 bare 的 4.58 Å 增至 poly 的 7.57 Å，并在 q=-2 poly 1 ns 中维持 8.46 Å。
3. AIMD/DFT 负责证明进入内层接触后发生 contact-gated reduction / Al-Mg incorporation。

因此 poly-APC 的优势不是体相离子传输，而是：**Si/O-rich POSS-derived interface 降低 Al 阴离子到达 Mg 电子转移前沿的概率，并降低 Al0/Mg-Al 共沉积副反应。**
