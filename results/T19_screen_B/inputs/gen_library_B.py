# -*- coding: utf-8 -*-
"""Deterministic generator for the Screen-B (T19) Round-1 candidate library.
Two axes: (A) cured network/passivator chemistries (vary backbone heteroatom +
substituent), screened with the APC anion fixed; (B) reducible-anion families,
screened with the POSS network fixed. Output is a SPEC list -- EPYC builds the
structures. No randomness/dates (reproducible)."""
import csv, os, hashlib

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library_round1.csv")
rows = []
def add(cls, family, motif, variant, cured_phase, anion, verdict, tier1, tier2):
    rows.append(dict(cand_id="", cls=cls, family=family, motif=motif, variant=variant,
                     cured_phase=cured_phase, anion_fixed_or_target=anion,
                     predicted_verdict=verdict, tier1_D1_D3p_D4p=tier1, tier2_D2=tier2))

# ---------- Axis A: network / passivator chemistries (anion fixed = [AlPh2Cl2]-) ----------
NET = [
 ("silsesquioxane","Si-O-Si","SiO2",
   ["H","methyl","vinyl","phenyl","aminopropyl","glycidoxy","mercaptopropyl","trifluoropropyl"],
   "reference / strong (POSS = validated hit)"),
 ("borosiloxane","B-O-Si","borosilicate (B2O3.SiO2)",
   ["B:Si=1:3","B:Si=1:1","B:Si=3:1"],
   "predicted STRONG (wide gap + Lewis-acid Cl/anion binding)"),
 ("phosphazene","P=N","phosphorus oxynitride (PON/P3N5)",
   ["chloro","phenoxy","trifluoroethoxy","dimethylamino"],
   "moderate"),
 ("polyether-siloxane","C-O-C/Si-O","SiO2 + ether",
   ["EO2","EO4","EO8"],
   "moderate; ether-O may lower D4 (Mg2+ coordination)"),
 ("carbosilane","Si-C","SiOC/SiC",
   ["methylene","ethylene","phenylene"],
   "leaky risk (narrower gap / C states)"),
 ("titanosiloxane","Ti-O-Si","TiO2.SiO2",
   ["Ti:Si=1:4","Ti:Si=1:1"],
   "narrow-gap risk (TiO2 ~3 eV)"),
 ("zirconosiloxane","Zr-O-Si","ZrO2.SiO2",
   ["Zr:Si=1:4","Zr:Si=1:1"],
   "predicted STRONG (wide gap)"),
 ("phosphosilicate","P-O-Si","P2O5.SiO2",
   ["P:Si=1:4","P:Si=1:1"],
   "moderate"),
 ("germania network","Ge-O","GeO2",
   ["amorphous"],
   "narrow-gap risk"),
 ("aluminosiloxane / alumoxane","Al-O-Si / Al-O","Al2O3.SiO2 / Al2O3",
   ["Al:Si=1:4","Al:Si=1:1","pure Al-O"],
   "FAIL control (Al-rich -> leaky/metallic on reduction)"),
]
for fam, motif, phase, variants, verdict in NET:
    for v in variants:
        add("network", fam, motif, v, phase, "[AlPh2Cl2]-", verdict,
            "yes", "yes")

# ---------- Axis B: reducible-anion families (network fixed = POSS/SiO2) ----------
AN = [
 ("[AlPh2Cl2]-","APC dominant aluminate","reducible -1.9..-3.4 V; deposits Al0 (baseline)"),
 ("[AlPhCl3]-","APC aluminate","reducible; deposits Al0"),
 ("[AlPh3Cl]-","APC aluminate","reducible; deposits Al0"),
 ("[AlCl4]-","inorganic Mg-Al chloride","reducible; deposits Al0"),
 ("[BH4]-","borohydride (non-Al)","transferability test (no metal co-deposition expected)"),
 ("[B(OCH(CF3)2)4]-","fluorinated borate","off-narrative COMPARATOR only (screened, not claimed)"),
 ("[CB11H12]-","carborane (weakly coordinating)","transferability test"),
 ("[TFSI]-","bis(trifluoromethanesulfonyl)imide","off-narrative COMPARATOR only (screened, not claimed)"),
 ("[B(C6F5)4]-","perfluoroaryl borate","off-narrative COMPARATOR only (screened, not claimed)"),
]
for an, fam, verdict in AN:
    add("anion", fam, "anion redox", an, "SiO2 (POSS, fixed)", an, verdict,
        "yes", "n/a (anion axis: D1 only)")

# ---------- assign IDs, write ----------
for i, r in enumerate(rows, 1):
    r["cand_id"] = f"B{i:03d}"
cols = ["cand_id","cls","family","motif","variant","cured_phase",
        "anion_fixed_or_target","predicted_verdict","tier1_D1_D3p_D4p","tier2_D2"]
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for r in rows: w.writerow(r)

h = hashlib.sha256(open(OUT, "rb").read()).hexdigest()[:12]
n_net = sum(1 for r in rows if r["cls"]=="network")
n_an  = sum(1 for r in rows if r["cls"]=="anion")
print(f"library_round1.csv  N={len(rows)}  (networks={n_net}, anions={n_an})  sha256:{h}")
print("Tier1 (EPYC molecular DFT): all", len(rows))
print("Tier2 (EPYC periodic DFT): networks", n_net)
