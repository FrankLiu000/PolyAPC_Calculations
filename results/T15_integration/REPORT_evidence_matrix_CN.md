# poly-APC Mg/Al共沉积计算证据矩阵

日期：2026-07-01
目的：把 classical-MD、MLFF-MD、AIMD/DFT 三条计算线放到同一张证据图里，明确哪些已经能写、哪些只是支持、哪些仍是发表级缺口。

## 当前结论

计算主线已经收敛到同一个机制：**poly-APC 的优势不是体相Mg离子传输，而是界面组成/氧化还原选择性优势**。POSS-derived Si/O-rich、Al-poor界面降低 Al 阴离子/Al中心进入 Mg 电子转移前沿的机会，并避免 bare 中 Al0/Mg-Al 异质核扰乱 Mg 同质外延。

但严格说，当前仍不能把计算结论写成“已发表级直接观察到 spontaneous Al plating”。原因是：

- classical-MD 只能给 contact-opportunity，不能给 Al0；
- 旧 T17 MLFF-MD 给长时间 Al-center standoff，但仍是 pre-r8 support，不是 key-reactive gated production；
- T23 AIMD 已有 near-contact + low-qAl + dechlorination support，但 strict slab-contact 和 3 seeds x 3 ps publication gate 未过；
- Mg(0002) texture 的直接模拟需要 r8mgdep 轨迹包含显式新沉积 Mg，当前只准备好了 matched seed 和分析器。

## 证据分层

| 层级 | 已有证据 | 可写进主线的句子 | 不能写的句子 |
|---|---|---|---|
| DFT | APC Al物种可还原，Al-Cl cleavage/Al-in-Mg alloying有化学可行性 | Al-containing APC species can lead to Al0/Mg-Al once productive contact occurs | DFT alone proves spontaneous plating in the full interface |
| classical-MD | cathode 1.0 nm层中 bare Al center 0.310 vs poly 0.0895 /nm2；Al+Cl 0.959 vs 0.221 /nm2 | poly lowers Al-center/reactive-site contact opportunity at Mg cathode | classical-MD observes electron transfer or Al0 |
| MLFF-MD pre-r8 | matched neutral 400 ps production: bare Al_slabMin 4.58 A, poly 7.57 A；poly q=-2 1 ns remains 8.46 A | poly keeps reducible Al center away from the 3D Mg front | this is direct Al0/Mg-Al co-deposition |
| AIMD T23 | bare near-contact + low-qAl + nCl<=1 auxiliary gate passed in two seeds | once Al-anion reaches Mg, AIMD supports contact-gated reduction/dechlorination | publication-ready spontaneous plating is already complete |
| r8/post-r8 | r8 training and key holdout gate prepared; production runners and summarizer ready | after gate passes, r8 production can become publication MLFF evidence | production can be launched before gate or interpreted if it fails |
| Mg texture | cryo-EM bridge and explicit Mg-deposit texture probe prepared | Al/Mg-Al foreign co-deposit is the computational mechanism for bare disorder | current Al-anion T17 trajectories directly prove Mg(0002) texture |

## Machine-Readable Matrix

The CSV table is:

```text
results/T15_integration/evidence_matrix_20260701.csv
```

## Figure/Story Logic

```text
classical-MD:
  bare has more Al-center / Al-Cl contact opportunity at cathode
  poly lowers cathode reactive-site density

MLFF-MD:
  bare Al center stays near the Mg front
  poly Al center remains farther away, including q=-2 negative control

AIMD/DFT:
  if Al-anion reaches contact, reduction/dechlorination/Al-Mg incorporation is chemically plausible
  T23 is currently support-level and still extending to publication gate

cryo-EM texture:
  bare Al/Mg-Al heterogeneity disrupts Mg homoepitaxy
  poly Al-poor interface preserves Mg(0002)-oriented growth
```

## Publication Gate Still Open

Minimum evidence still needed before marking the computation complete:

1. **AIMD:** T23 must reach strict slab-contact + low-qAl publication gate or produce a clearly justified alternative with replicated release windows and matched poly negative controls.
2. **MLFF-MD:** r8 key holdout must pass; only then run matched bare/poly `r8neutral` and `r8mgdep` production.
3. **DFT validation:** any post-r8 candidate Al plating/dechlorination frames must be sent back to CPU DFT/AIMD labels before being used as final evidence.
4. **Texture:** Mg(0002) claim must be based on trajectories with explicit new deposited Mg indices, reported as change vs matched seed baseline.

This keeps the manuscript language honest: current computation strongly supports **Al access/selectivity gating** and **Al-as-foreign-codeposit texture disruption**, while direct publication-grade Mg/Al co-deposition remains gated by T23/r8 completion.
