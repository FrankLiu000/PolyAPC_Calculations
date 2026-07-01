# Post-r8 T17 co-deposition / Mg texture summary

本报告只汇总带有 `*_done.json` 的 post-r8 轨迹；缺失、失败或部分轨迹不会被当作证据。
tail fraction: 0.5

## 当前状态

尚无完成的 `r8neutral` 或 `r8mgdep` production run。等待 r8 key-holdout gate 通过后再启动 gated runners。

## Interpretation guardrail

- `Al_codeposition_proxy_frac = Al_slabMin_A < 3.2 A 且 Al_nCl <= 1`，是 MLFF-MD 中的还原/共沉积几何代理，仍需 DFT/AIMD holdout 佐证。
- Mg(0002)织构指标只对 `r8mgdep` probe 有意义，且报告末段相对 seed baseline 的变化；初态本身不作为 poly 优势证据。
- 若 bare 显示更高 codep proxy / near4-deCl，而 poly 保持更低 Al 接触并更好维持 Mg texture，才可作为 cryo-EM Mg(0002)差异的计算对应。
