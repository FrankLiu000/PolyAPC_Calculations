# Angewandte manuscript figure package (poly-APC)

Submission-grade figures for the Angew Chem Int Ed Research Article
*"A Silicon-Rich, Aluminum-Poor Interphase … Enables Reversible Magnesium Metal Anodes."*

Built to the [Angew graphics guidelines](https://onlinelibrary.wiley.com/page/journal/15213773/homepage/graphics-guidelines):
Arial 7–8 pt; double-column 17.2 cm (≤17.8 max); closed boxes, ticks-in; **CVD-safe Okabe–Ito palette**
+ shape/hatch coding (grayscale-robust per §5); vector PDF/SVG (line-art ≥1000 dpi) + 300-dpi PNG;
**TIFF→CMYK** regenerable via `scripts/angew_style.py:save_pub`. **No AI-generated imagery** — every panel is a
scripted plot of measured/computed data; molecular structures are ball-and-stick renders of DFT/MD `.xyz`.

## figures/
| File | Content | Style ref |
|---|---|---|
| Fig1_electrolyte_redox | cation + anion 3D structures, Schlenk speciation, redox ladder vs Mg | JPCC (structures+energetics) |
| Fig2_performance | Mo₆S₈ cap+CE/cycle (0.5C,1C), V-profiles@cycles, Mg‖Mg V–t | Li Angew Fig 5 |
| Fig3_interphase | XPS at% stacked bar, ToF-SIMS log-depth, **3D ion maps**, XPS Al 2p scatter+fits, at%/metallic | Li Angew Fig 3 |
| Fig3b_XPS_multielement | Al/Si/Cl/Mg/O/C core levels × bare/poly × 3 depths (scatter + GL fits) | battery-SEI XPS |
| Fig4_deposit | XRD texture, EDS ratios, SEM, EDS Al-Kα maps *(+cross-section TONIGHT, cryo-EM MON)* | Li Angew Fig 4 |
| Fig5_computation | interface MD box, Al-in-Mg slab, reduction ΔG, **SEI DOS**, network sequestration, XPS/Raman validation | JPCC (structures+DOS) |

> **Fig 5d upgrade pending:** band-gap bars → real **DOS/PDOS curves** once `results/T8b_DOS/` lands from EPYC
> (see `results/T8b_DOS/REQUEST_EPYC.md`).

## scripts/  (provenance; absolute data paths → run on the Windows analysis box)
`angew_style.py` (shared style + CMYK export), `mol_render.py` (xyz ball-and-stick, no ASE),
`xps_helper.py` (scatter+Shirley+GL fit), `fig2/fig3/fig15/fig_xps.py` (figures),
`agg_mo6s8.py`/`retention.py`/`extract_profiles.py` (module-O cycling re-processing).

## element_maps/  EDS Kα maps extracted+identified from the SEM+EDS docx (area2=poly, area3=bare)
Mg, O, Cl, Al, C (+ Si = GF/D glass-fibre artifact, kept for completeness), layered, SEM. Genuine Al/Cl/Mg/O;
**Si is a separator artifact — Si-enrichment is a ToF-SIMS result.**

## mo6s8_cycling/  module-O analysis (per-cycle capacity/CE), >80% retention: poly 842cyc@0.5C / 1592cyc@1C.
