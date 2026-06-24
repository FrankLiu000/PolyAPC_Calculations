# -*- coding: utf-8 -*-
"""
Fig 4 - Deposit morphology and composition (poly-APC vs bare-APC plated Mg on Cu).
Re-framed for the "uneven-stripping" narrative: morphology now matters, with a NEW
cross-section panel after 30 cycles. Always bare vs poly in parallel.

Panel set (target):
  (a) XRD texture of plated Mg     - real scan CSVs; A002/A101 = 0.83 poly vs 0.39 bare; hcp Mg, no crystalline Al.
  (b) Top-view SEM matched mag     - bare rough/granular vs poly dense/conformal (TIFFs, calibrated scale bars).
  (c) Cross-section after 30 cycles- bare porous/swollen vs poly dense  (NEW data; uneven-stripping failure).
  (d) EDS composition              - bare vs poly bars + Cl/Mg x23, Al/Mg x7 folds; Si bar = glass-fibre artifact (NOT POSS).
  (+) compact EDS map strip Mg/Cl/Al (bare+poly).

CRITICAL labelling constraints (locked):
  - EDS Si = GF/D borosilicate glass-fibre separator ARTIFACT, NOT the POSS interphase
    (Si-rich-interphase claim rests on ToF-SIMS in Fig 3, not EDS).
  - No fluorine / MgF2 narrative.

Sources:
  XRD  : XRD_deposited_Mg/analysis_output/scan_{bareAPC,polyAPC}.csv  (2theta, raw, bg_sub, bg_sub_smoothed)
         texture ratios verified in XRD_deposited_Mg/results/summary_xrd.json
  SEM  : SEM+EDS_MgCu_cell/20260623/*.tif  (Hitachi SU-8010, 3 kV; scale from per-file PixelSize)
  EDS  : SEM+EDS_MgCu_cell/results/figs/*map_*.png (cropped tiles) + results/eds_composition.csv
Reuses the data-loading logic of make_Fig4_deposit.py / make_morphology_figure.py / make_SEM_EDS_figure.py.

Run:  python fig4_deposit.py
"""
import os
import sys
import csv
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from PIL import Image

# ---- shared Angew style (Arial, closed boxes, CMYK-safe palette, save_pub) ----
STYLE_DIR = r"C:/Users/刘悦铮/AppData/Local/Temp/claude/D--20260602-polyAPC-data/302d1e65-667d-4649-a77b-21f3a1304446/scratchpad"
sys.path.insert(0, STYLE_DIR)
from angew_style import W2, C, save_pub, panel_label  # noqa: E402

# -------- absolute data roots --------
DATA = r"D:/20260602_polyAPC_data"
TIF = os.path.join(DATA, "SEM+EDS_MgCu_cell", "20260623")
FIGS = os.path.join(DATA, "SEM+EDS_MgCu_cell", "results", "figs")
EDS_CSV = os.path.join(DATA, "SEM+EDS_MgCu_cell", "results", "eds_composition.csv")
XRD = os.path.join(DATA, "XRD_deposited_Mg", "analysis_output")
OUT = os.path.join(DATA, "Angewandte_Research_Article", "figures", "Fig4_deposit")

POLY = C["poly"]   # blue   - protagonist
BARE = C["bare"]   # orange - control
BARE_T = C["bare_d"]  # dark orange for text on white

# ============================================================
#  data loaders (reused from existing builders)
# ============================================================
def load_xrd(name):
    """name in {bareAPC, polyAPC} -> ndarray cols [2theta, raw, bg_sub, bg_sub_smoothed]."""
    rows = []
    with open(os.path.join(XRD, f"scan_{name}.csv")) as f:
        r = csv.reader(f); next(r)
        for row in r:
            rows.append([float(x) for x in row])
    return np.array(rows)


def load_eds():
    """eds_composition.csv -> dict[(electrolyte, element)] = (wt_pct, wt_sigma, at_pct)."""
    d = {}
    with open(EDS_CSV) as f:
        for row in csv.DictReader(f):
            d[(row["electrolyte"], row["element"])] = (
                float(row["wt_pct"]), float(row["wt_sigma"]), float(row["at_pct"]))
    return d


# ---- SEM TIFF helpers (calibrated scale bar from PixelSize; crop SU8010 data bar) ----
def pixsize_nm(stem):
    for line in open(os.path.join(TIF, stem + ".txt"), encoding="latin-1"):
        if line.startswith("PixelSize="):
            return float(line.split("=")[1])
    return None


def databar_top(a):
    med = np.median(a, axis=1); H = a.shape[0]; y = H - 1
    while y > 0 and med[y] < 50:
        y -= 1
    return y + 1 if (H - (y + 1)) < 0.22 * H else H


def show_sem(ax, stem, scalebar_um, frame, label=None, sublabel=None, crop_frac=None):
    a = np.array(Image.open(os.path.join(TIF, stem + ".tif")).convert("L"))
    a = a[:databar_top(a)]
    if crop_frac:  # (top,bottom,left,right) fractions to keep
        H, W = a.shape
        t, b, l, r = crop_frac
        a = a[int(t * H):int(b * H), int(l * W):int(r * W)]
    ax.imshow(a, cmap="gray", vmin=0, vmax=255)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(True); s.set_linewidth(1.0); s.set_color(frame)
    umpp = pixsize_nm(stem) / 1000.0
    H, W = a.shape
    barpx = scalebar_um / umpp
    x1 = W * 0.955; x0 = x1 - barpx; y = H * 0.93
    ax.plot([x0, x1], [y, y], color="white", lw=2.6, solid_capstyle="butt")
    ax.text((x0 + x1) / 2, y - H * 0.035, f"{scalebar_um:g} µm", color="white",
            ha="center", va="bottom", fontsize=6.0, fontweight="bold")
    if label:
        ax.text(0.035, 0.95, label, transform=ax.transAxes, color="white",
                ha="left", va="top", fontsize=7.4, fontweight="bold")
    if sublabel:
        ax.text(0.035, 0.045, sublabel, transform=ax.transAxes, color="white",
                ha="left", va="bottom", fontsize=6.0)


# ---- EDS map tiles (composite RGBA on white; trim transparent title strip) ----
def eds_tile(fn, pad=2):
    full = Image.open(os.path.join(FIGS, fn)).convert("RGBA")
    a = np.array(full); alpha = a[:, :, 3]
    ys, xs = np.where(alpha > 0)
    t, b, l, r = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    cov = (alpha > 0).mean(axis=1); rows = np.where(cov > 0.5)[0]
    if len(rows):
        t = rows.min()
    bg = Image.new("RGBA", full.size, (255, 255, 255, 255))
    img = np.array(Image.alpha_composite(bg, full).convert("RGB"))
    t = max(0, t - pad); l = max(0, l - pad)
    b = min(img.shape[0], b + pad); r = min(img.shape[1], r + pad)
    return img[t:b, l:r]


def show_eds(ax, fn, frame, title=None):
    ax.imshow(eds_tile(fn)); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(True); s.set_linewidth(0.8); s.set_color(frame)
    if title:
        ax.set_title(title, fontsize=7.0, pad=1.5)


# ============================================================
#  figure
# ============================================================
eds = load_eds()
t_bare = load_xrd("bareAPC")
t_poly = load_xrd("polyAPC")

fig = plt.figure(figsize=(W2, 9.55))
# rows: a(XRD) | b(top-view) | c(cross-section) | d(EDS bars) | EDS-map strip
gs = fig.add_gridspec(
    5, 12,
    height_ratios=[1.28, 1.18, 1.05, 1.30, 1.02],
    hspace=0.46, wspace=0.16,
    left=0.075, right=0.985, top=0.967, bottom=0.052,
)

# -------------------------------------------------------------------------
# (a) XRD texture of plated Mg  (real scans; bg-sub smoothed, offset overlay)
# -------------------------------------------------------------------------
axa = fig.add_subplot(gs[0, 0:12])
col_xrd_b, col_xrd_p = 3, 3  # bg_sub_smoothed
off = 9000.0
axa.plot(t_poly[:, 0], t_poly[:, col_xrd_p] + off, color=POLY, lw=1.0, label="poly-APC")
axa.plot(t_bare[:, 0], t_bare[:, col_xrd_b], color=BARE, lw=1.0,
         ls=(0, (5, 2)), label="bare-APC")
# Mg hcp reference lines (Cu Kalpha) - only those within the 28-50 deg window
MG = {"(100)": 32.19, "(002)": 34.40, "(101)": 36.62, "(102)": 47.80}
for h, p in MG.items():
    axa.axvline(p, color="#888", ls=":", lw=0.55, alpha=0.7)
    axa.text(p, off * 2.07, f"Mg{h}", color="#555", fontsize=5.0,
             rotation=90, va="top", ha="center")
# Al(111) reference - explicitly absent (no crystalline Al / Mg-Al alloy)
axa.axvline(38.47, color=C["green"], ls="-.", lw=0.7, alpha=0.8)
axa.text(38.9, off * 1.62, "Al(111) 38.5°\nabsent", color=C["green"],
         fontsize=5.4, va="center", ha="left", fontweight="bold")
axa.set_xlim(28, 50)
axa.set_ylim(-700, off * 2.18)
axa.set_yticks([])
axa.set_xlabel("2θ (degree, Cu Kα)")
axa.set_ylabel("Intensity (a.u.)")
axa.tick_params(top=False)
# texture annotation (verified ratios from summary_xrd.json)
axa.text(0.985, 0.93,
         "Mg(002)/(101) texture\n"
         "poly 0.83  vs  bare 0.39\n"
         "(both hcp Mg; no crystalline Al)",
         transform=axa.transAxes, ha="right", va="top", fontsize=6.0,
         color=C["ink"],
         bbox=dict(boxstyle="round,pad=0.30", fc="white", ec="#BBB", lw=0.6))
leg_a = axa.legend(loc="upper left", fontsize=6.6, handlelength=1.6,
                   bbox_to_anchor=(0.005, 0.99))
leg_a.get_frame().set_visible(False)
panel_label(axa, "a", x=-0.058, y=1.02)
axa.set_title("XRD of plated Mg @ separator", fontsize=7.6, pad=2, loc="left")

# -------------------------------------------------------------------------
# (b) Top-view SEM, matched magnification: bare 2k/20k | poly 2k/20k
# -------------------------------------------------------------------------
TV = [("bare_3", 10, BARE, "bare-APC", "×2k"),
      ("bare_5", 2, BARE, "bare-APC", "×20k"),
      ("poly_1", 10, POLY, "poly-APC", "×2k"),
      ("poly_3", 2, POLY, "poly-APC", "×20k")]
axb0 = None
for i, (stem, sb, fr, lab, mag) in enumerate(TV):
    ax = fig.add_subplot(gs[1, 3 * i:3 * i + 3])
    show_sem(ax, stem, sb, fr, label=lab, sublabel=mag)
    if i == 0:
        axb0 = ax
yb = axb0.get_position().y1 + 0.004
fig.text(0.075, yb, "b", fontsize=10, fontweight="bold", ha="left", va="bottom")
fig.text(0.098, yb, "Top-view morphology (matched magnification)",
         fontsize=7.6, fontweight="bold", ha="left", va="bottom")
fig.text(0.985, yb,
         "bare: rough / granular / nodular      poly: smooth / dense / conformal",
         fontsize=6.0, ha="right", va="bottom", color="#444")

# -------------------------------------------------------------------------
# (c) Cross-section after 30 cycles (NEW): bare porous/swollen | poly dense
# -------------------------------------------------------------------------
axc1 = fig.add_subplot(gs[2, 0:6])
show_sem(axc1, "bare-Xsection_7", 50, BARE, label="bare-APC")
axc2 = fig.add_subplot(gs[2, 6:12])
show_sem(axc2, "poly-Xsection_4", 50, POLY, label="poly-APC")
axc1.text(0.5, -0.085, "porous / swollen, ~120–170 µm",
          transform=axc1.transAxes, ha="center", va="top", fontsize=6.0, color=BARE_T)
axc2.text(0.5, -0.085, "dense, compact deposit",
          transform=axc2.transAxes, ha="center", va="top", fontsize=6.0, color=POLY)
yc = axc1.get_position().y1 + 0.004
fig.text(0.075, yc, "c", fontsize=10, fontweight="bold", ha="left", va="bottom")
fig.text(0.098, yc, "Cross-section after 30 cycles",
         fontsize=7.6, fontweight="bold", ha="left", va="bottom")
fig.text(0.985, yc,
         "vs 77 µm dense-Mg theoretical $\\Rightarrow$ uneven stripping / swelling",
         fontsize=6.0, ha="right", va="bottom", color="#444")

# -------------------------------------------------------------------------
# (d) EDS composition: bare vs poly bars + Cl/Mg x23, Al/Mg x7 folds
# -------------------------------------------------------------------------
elems = ["C", "O", "Mg", "Al", "Si", "Cl"]
bare_at = [eds[("bare-APC", e)][2] for e in elems]
poly_at = [eds[("poly-APC", e)][2] for e in elems]

axd = fig.add_subplot(gs[3, 0:8])
x = np.arange(len(elems)); w = 0.38
b_bare = axd.bar(x - w / 2, bare_at, w, color=BARE, label="bare-APC",
                 edgecolor="white", linewidth=0.4)
b_poly = axd.bar(x + w / 2, poly_at, w, color=POLY, label="poly-APC",
                 edgecolor="white", linewidth=0.4)
# hatch the Si pair to mark it as the glass-fibre artifact
i_si = elems.index("Si")
for xb, hv in [(x[i_si] - w / 2, bare_at[i_si]), (x[i_si] + w / 2, poly_at[i_si])]:
    axd.bar(xb, hv, w, fill=False, hatch="////", edgecolor="#444", linewidth=0.0)
axd.set_xticks(x); axd.set_xticklabels(elems)
axd.set_ylabel("EDS composition (at %)")
axd.set_ylim(0, 50)
axd.spines[["top", "right"]].set_visible(False)
axd.tick_params(top=False, right=False)
leg_d = axd.legend(fontsize=6.6, ncol=2, loc="upper right", handlelength=1.1)
leg_d.get_frame().set_visible(False)
# Si artifact callout
axd.annotate("Si = glass-fibre artifact\n(borosilicate separator, NOT POSS)",
             xy=(x[i_si], max(bare_at[i_si], poly_at[i_si]) + 0.6),
             xytext=(x[i_si] - 0.35, 18.5),
             ha="center", va="bottom", fontsize=5.7, color="#333",
             arrowprops=dict(arrowstyle="->", color="#555", lw=0.7))
# key Mg-rich vs Cl/Al-rich callouts
axd.text(x[2] + w / 2, poly_at[2] + 0.8, f"{poly_at[2]:.0f}", ha="center",
         va="bottom", fontsize=5.8, color=POLY, fontweight="bold")
panel_label(axd, "d", x=-0.105, y=1.02)
axd.set_title("EDS quantification (area-sum)", fontsize=7.6, pad=2, loc="left")

# fold sub-panel: bare/poly atomic ratios (log) -> Cl/Mg x23, Al/Mg x7
axe = fig.add_subplot(gs[3, 9:12])
rl = ["Cl/Mg", "Al/Mg"]
bare_r = [bare_at[elems.index("Cl")] / bare_at[2], bare_at[3] / bare_at[2]]
poly_r = [poly_at[elems.index("Cl")] / poly_at[2], poly_at[3] / poly_at[2]]
xr = np.arange(2)
axe.bar(xr - w / 2, bare_r, w, color=BARE, edgecolor="white", linewidth=0.4)
axe.bar(xr + w / 2, poly_r, w, color=POLY, edgecolor="white", linewidth=0.4)
axe.set_yscale("log")
axe.set_xticks(xr); axe.set_xticklabels(rl)
axe.set_ylabel("atomic ratio (log)")
axe.set_ylim(0.02, 3)
axe.spines[["top", "right"]].set_visible(False)
axe.tick_params(top=False, right=False)
for i, (br, pr) in enumerate(zip(bare_r, poly_r)):
    axe.text(i, max(br, pr) * 1.7, f"×{br/pr:.0f}", ha="center", va="bottom",
             fontsize=6.6, fontweight="bold", color=C["ink"])
axe.set_title("bare/poly fold", fontsize=6.6, color="#333", pad=2)

# -------------------------------------------------------------------------
# compact EDS map strip: Mg / Cl / Al  (bare row + poly row)
# -------------------------------------------------------------------------
MAP_KEYS = [("mgmap_{s}.png", "Mg"), ("clmap_{s}.png", "Cl"), ("almap_{s}.png", "Al")]
ax_strip0 = None
for col, (tmpl, head) in enumerate(MAP_KEYS):
    # bare in left half (cols 0-5), poly in right half (cols 6-11); 2 columns each tile
    axb_ = fig.add_subplot(gs[4, 2 * col:2 * col + 2])
    show_eds(axb_, tmpl.format(s="bare"), BARE, title=head)
    axp_ = fig.add_subplot(gs[4, 6 + 2 * col:6 + 2 * col + 2])
    show_eds(axp_, tmpl.format(s="poly"), POLY, title=head)
    if col == 0:
        ax_strip0 = axb_
        ax_poly0 = axp_
        axb_.text(-0.13, 0.5, "bare", transform=axb_.transAxes, rotation=90,
                  va="center", ha="right", color=BARE_T, fontsize=6.6, fontweight="bold")
        axp_.text(-0.13, 0.5, "poly", transform=axp_.transAxes, rotation=90,
                  va="center", ha="right", color=POLY, fontsize=6.6, fontweight="bold")
# header placed well clear of the per-tile element titles
ys = ax_strip0.get_position().y1 + 0.026
fig.text(0.075, ys, "e", fontsize=10, fontweight="bold", ha="left", va="bottom")
fig.text(0.098, ys, "EDS element maps", fontsize=7.6, fontweight="bold",
         ha="left", va="bottom")
fig.text(0.985, ys, "Si map omitted (glass-fibre artifact → SI)",
         fontsize=6.0, ha="right", va="bottom", color="#444")

# -------------------------------------------------------------------------
# footer
# -------------------------------------------------------------------------
fig.text(0.075, 0.004,
         "Plated Mg on Cu, 30 mAh cm$^{-2}$ / 30 cycles. SEM+EDS: Hitachi SU-8010, 3 kV "
         "(scale bars from PixelSize; EDS area-sum, semi-quant, ratios robust). "
         "XRD: Cu K$\\alpha$, bg-subtracted. "
         "Si tracks the GF/D borosilicate glass-fibre separator (artifact), NOT POSS; "
         "the Si-rich interphase claim rests on ToF-SIMS (Fig. 3).",
         fontsize=5.2, color="#666", ha="left", va="bottom")

save_pub(fig, OUT, dpi_tiff=600)
plt.close(fig)
print("Fig4_deposit built ->", OUT)
print("  bare at%% Cl/Mg=%.3f Al/Mg=%.3f -> folds x%.0f / x%.0f"
      % (bare_r[0], bare_r[1], bare_r[0] / poly_r[0], bare_r[1] / poly_r[1]))
