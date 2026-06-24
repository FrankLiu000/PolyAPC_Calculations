# § O. Mg‖Mo₆S₈ full-cell galvanostatic cycling (0.5C + 1C) — capacity retention & life

**Created:** 2026-06-23 · module **O** (was pending). **Node:** exp/wet (Neware).
**Data:** raw Neware GBK per-point `.txt` exports —
- 0.5C: `MgMo6S8 LE 0.5C_033_6.txt` (**LE = bare-APC**), `MgMo6S8 SPE 0.5C_032_5.txt` (**SPE = poly-APC**)
- 1C: `MgMo6S8_polyAPC.txt` (**poly-APC**; no bare 1C run supplied)

**Cell:** Mg ‖ APC (bare/poly) ‖ **Mo₆S₈ (Chevrel)** full cell. **Convention:** discharge = Mg²⁺ insertion into Mo₆S₈; specific capacity (mAh g⁻¹) from the instrument 比容量 column; CE = discharge/charge per cycle. Cycles **1–4 = formation** (1st-cycle CE ≈ 130–155 %, conversion/irreversible); **reversible cycling from cycle 5** (CE → ~100 %). Capacity **retention referenced to the maximum reversible discharge capacity (cycles ≥ 5)**, per common practice — *not* to the inflated formation cycle 1.

## O.1 Key numbers (bare ‖ poly)
| Metric | bare-APC 0.5C | poly-APC 0.5C | poly-APC 1C |
|---|---:|---:|---:|
| Reversible capacity (ref, cyc 5), mAh g⁻¹ | 49.8 | **58.9** | 48.7 |
| **Cycles with retention > 80 %** | **269** | **842 (full run)** | **1592 (≈1600)** |
| Capacity at end of >80 % window, mAh g⁻¹ | 39.8 | 46.8 | 39.0 |
| Mean CE in >80 % window, % | 99.6 | 99.95 | ~100.0 |
| Total cycles recorded | 10002* | 842 | 3344 |
| Capacity at cyc 500 (% of ref) | 47.0 % | 92.7 % | 84.6 % |
| Capacity at cyc 800 (% of ref) | **5.0 %** | **84.4 %** | 84.0 % |
| Fate beyond window | **collapses to ≈0 (0.1 mAh g⁻¹ by ~cyc 700–1000)** | still > 80 % at run end | slow fade (70 % @2000, 23 % @3000) |

\* bare's 10002 "cycles" are post-death coulombic noise (capacity ≈ 0.1 mAh g⁻¹); the cell is functionally dead after ~700 cycles.

## O.2 Reading — the battery headline (per PI: report only the poly >80 % window)
1. **poly-APC sustains long, reversible Mg‖Mo₆S₈ cycling; bare-APC fades fast.** At **0.5C**, poly holds **>80 % capacity retention across the entire 842-cycle run** (still going) at CE ≈ 100 %, whereas bare drops below 80 % by **cycle 269** and **collapses to ≈0 by ~cycle 700**. At **1C**, poly holds **>80 % for ~1600 cycles (1592)** at CE ≈ 100 %.
2. **CE ≈ 100 % within the window** for poly (vs bare's irreversible fade) — the full-cell counterpart of the reversibility story; replaces the dropped GITT CE metric as the headline.
3. **Not transport.** Both electrolytes show the same initial reversible capacity (~49–59 mAh g⁻¹) and identical rate-normalised plateaus; the divergence is **durability/reversibility**, consistent with the locked thesis (transport equal — MD + Bruce–Vincent; the win is the Si-rich/Al-poor interphase suppressing parasitic Al-anion reduction).

## O.3 Figures & artefacts
`results/figures/fig_Mo6S8_cycling.png` — (a) 0.5C poly vs bare capacity vs cycle (poly stable, bare death); (b) poly 1C capacity + CE vs cycle, truncated at the 80 %-retention cycle (1592). Per-cycle data: `results/data/percycle_{bare_0p5C,poly_0p5C}.csv` (+ `percycle_poly_1C.csv` under `MgMo6S8_1C_cycle/results/data/`); `retention_summary.json`, `summary.json`.

## O.4 Caveats
- Specific capacity uses the instrument 比容量 column (active-mass-normalised; nominal mass → absolute mAh g⁻¹ indicative, **ratios/retention/CE mass-independent**).
- One cell per electrolyte/rate; **no bare 1C run** supplied → 1C contrast is poly-only (life). The bare-vs-poly head-to-head is the **0.5C** pair.
- Retention reference = max reversible capacity (cyc ≥ 5); formation cycles 1–4 excluded. Reporting the poly **>80 % window only**, per PI (1C → ~1600 cyc; 0.5C → full 842 cyc).
- CE clipped to [95,101] % when averaging (instrument rounding gives occasional >100 %).

## O.5 Maps to article plan
`ARTICLE_PLAN_v3` Fig 2 (performance/longevity) — the **battery headline** that replaces GITT: poly long-life reversible full-cell cycling (0.5C 842 cyc >80 %; 1C ~1600 cyc >80 %) vs bare rapid death (~270 cyc). C1/C3/C6 (suppressed parasitic Al-anion redox → reversible cycling). Transport-equal null carried by §B (MD) + §N (Bruce–Vincent).
