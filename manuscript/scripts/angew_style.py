# -*- coding: utf-8 -*-
"""Shared Angewandte-compliant matplotlib style + export helpers.
Wiley/Angew graphics guidelines:
  - one-column 8.4 cm, two-column 17.8 cm (we target 17.2 cm to fit text block)
  - sans-serif (Arial), text 1.5-2 mm ~ 7-8 pt
  - line art >=1000 dpi (vector PDF/SVG covers this), raster >=300 dpi
  - colours defined in CMYK (not RGB) -> CMYK-safe palette + CMYK TIFF export
"""
import matplotlib as mpl
import matplotlib.pyplot as plt

CM = 1/2.54
W1 = 8.4*CM      # single column (in)
W2 = 17.2*CM     # double column (in), <= 17.8 cm max

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "font.size": 7.5,
    "axes.titlesize": 8.5,
    "axes.labelsize": 7.5,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 6.8,
    "axes.spines.right": True,   # closed box (battery-paper style)
    "axes.spines.top": True,
    "axes.linewidth": 0.9,
    "xtick.major.width": 0.9,
    "ytick.major.width": 0.9,
    "xtick.major.size": 3.2,
    "ytick.major.size": 3.2,
    "xtick.direction": "in",     # ticks inward
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "legend.frameon": False,
    "lines.linewidth": 1.3,
    "figure.dpi": 150,
})

# Colour-blind-safe, grayscale-robust palette (Okabe-Ito) per Angew §5 Mindful Colour:
# avoid red+blue+black+green clashes; differ by luminosity; pair with linestyle/marker/hatch.
# Primary contrast = blue (poly) vs orange (bare): CVD-safe AND separable in grayscale.
C = {
    "poly":   "#0072B2",   # blue   - protagonist (poly-APC)
    "poly2":  "#56B4E9",   # sky    - poly second series (1C)
    "bare":   "#E69F00",   # orange - control (bare-APC)
    "bare_d": "#9C6B00",   # dark orange (text)
    "accent": "#CC79A7",   # reddish-purple - tertiary (e.g. CE)
    "green":  "#009E73",   # bluish-green - Si / gain (used with hatch+label)
    "Al":     "#E69F00",   # orange - aluminium (categorical, label+hatch)
    "Si":     "#009E73",   # green  - silicon  (categorical, label+hatch)
    "red":    "#000000",   # reference/death cues -> BLACK line+style, not red (grayscale-safe)
    "ink":    "#222222",
    "grid":   "#E2E5EA",
}
# style/marker conventions so series survive grayscale (do not rely on colour alone)
STY = {
    "poly": dict(color=C["poly"],  linestyle="-",  marker="o"),
    "poly2":dict(color=C["poly2"], linestyle="-",  marker="^"),
    "bare": dict(color=C["bare"],  linestyle=(0,(5,2)), marker="s"),
    "ce":   dict(color=C["accent"],linestyle="none", marker="D"),
}
HATCH = {"Si": "///", "Al": "...", "poly": "///", "bare": "..."}

def panel_label(ax, s, x=-0.18, y=1.04, size=10):
    ax.text(x, y, s, transform=ax.transAxes, fontsize=size, fontweight="bold",
            va="bottom", ha="left")

def save_pub(fig, path_noext, dpi_tiff=600):
    """Save vector PDF+SVG (line-art compliant) and a CMYK TIFF + PNG preview."""
    fig.savefig(path_noext+".pdf", bbox_inches="tight")
    fig.savefig(path_noext+".svg", bbox_inches="tight")
    fig.savefig(path_noext+".png", dpi=300, bbox_inches="tight")
    # high-res TIFF then convert to CMYK per Angew colour rule
    tmp = path_noext+"_rgb.tiff"
    fig.savefig(tmp, dpi=dpi_tiff, bbox_inches="tight")
    try:
        from PIL import Image
        im = Image.open(tmp).convert("RGB").convert("CMYK")
        im.save(path_noext+".tiff", dpi=(dpi_tiff, dpi_tiff))
        import os; os.remove(tmp)
    except Exception as e:
        import os; os.replace(tmp, path_noext+".tiff")
        print("  [warn] CMYK convert skipped:", e)
    print("  saved:", path_noext, "(pdf/svg/png/tiff-CMYK)")
