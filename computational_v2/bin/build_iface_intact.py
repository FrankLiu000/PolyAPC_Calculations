#!/usr/bin/env python3
"""build_iface_intact.py <sys>   (sys = bare | poly)

Rebuild a clean interface start by transplanting the INTACT cation
[Mg2Cl3(THF)6]+ (correct geometry: Mg-Mg 3.87 A, 3 properly-bridging Cl) from the
validated seed PDB onto the slab, replacing the corrupted cation (atoms 64..146)
whose 3 Cl were stacked and whose Mg-Mg was a too-short 2.81 A.

Procedure:
  1. From the seed PDB take 2 Mg + 3 Cl + the 6 Mg-coordinated THF (drop 2 free THF)
     -> 83-atom cation, same count/order family as the interface block.
  2. Rigid-body place it: COM -> old cation COM; scan 3D orientations for the one
     that maximizes min-clearance to the environment (slab + anion + network).
  3. Reassemble  slab(0..63) + intact cation(83) + anion(147..171) + network(172..)
     so the anion still starts at index 147 (Al=147) and all analyses keep working.
Writes iface_<sys>_intact.coord.inc.
"""
import sys
import numpy as np

SEED = ("/CH/Claude_Calcs_20260603/classical_molecular_dynamics/handoff_for_agent/"
        "structures/representative_solvation/bare_octahedral_3Cl3O.pdb")
RCOV = {"H": 0.31, "C": 0.76, "O": 0.66, "Mg": 1.41, "Al": 1.21, "Cl": 1.02,
        "Si": 1.11, "F": 0.57, "S": 1.05}
CELL = ("    &CELL\n      A   12.836    0.000    0.000\n"
        "      B    6.418   11.116    0.000\n      C    0.000    0.000   55.000\n"
        "      PERIODIC XYZ\n    &END CELL\n")


def read_pdb(path):
    els, xyz = [], []
    for l in open(path):
        if l[:6] in ("ATOM  ", "HETATM"):
            els.append(l[76:78].strip())
            xyz.append([float(l[30:38]), float(l[38:46]), float(l[46:54])])
    return els, np.array(xyz)


def read_inc(path):
    syms, xyz, inb = [], [], False
    for l in open(path):
        s = l.strip()
        if s.startswith("&COORD"): inb = True; continue
        if s.startswith("&END COORD"): inb = False; continue
        if inb:
            t = s.split(); syms.append(t[0]); xyz.append([float(v) for v in t[1:4]])
    return syms, np.array(xyz)


def components(els, xyz, mask):
    """connected components among atoms where mask is True (covalent-radius bonds)"""
    idx = np.where(mask)[0]
    n = len(idx)
    pos = xyz[idx]; r = np.array([RCOV[els[i]] for i in idx])
    d = np.linalg.norm(pos[:, None] - pos[None], axis=2)
    bond = d < 1.3 * (r[:, None] + r[None])
    comp = np.full(n, -1); c = 0
    for i in range(n):
        if comp[i] >= 0: continue
        st = [i]; comp[i] = c
        while st:
            j = st.pop()
            for k in np.where(bond[j] & (comp < 0))[0]:
                comp[k] = c; st.append(k)
        c += 1
    return [idx[comp == k] for k in range(c)]


def extract_cation(els, xyz):
    els = np.array(els)
    mg = np.where(els == "Mg")[0]
    cl = np.where(els == "Cl")[0]
    org = np.where((els == "C") | (els == "O") | (els == "H"))[0]
    mask = np.zeros(len(els), bool); mask[org] = True
    thfs = components(els, xyz, mask)
    # rank THF rings by O-to-nearest-Mg distance; keep 6 coordinated
    def odist(comp):
        o = [i for i in comp if els[i] == "O"][0]
        return min(np.linalg.norm(xyz[o] - xyz[mg[0]]), np.linalg.norm(xyz[o] - xyz[mg[1]]))
    thfs = sorted(thfs, key=odist)[:6]
    order = list(mg) + list(cl)
    for t in thfs:
        # O first then C then H within each THF (purely cosmetic)
        order += sorted(t, key=lambda i: {"O": 0, "C": 1, "H": 2}[els[i]])
    cat_syms = [els[i] for i in order]
    cat_xyz = xyz[order]
    assert len(order) == 83, "cation must be 83 atoms, got %d" % len(order)
    return cat_syms, cat_xyz


def rand_rotations(n=4000):
    """deterministic ~uniform SO(3) grid via golden-spiral axes x angles (no RNG)."""
    rots = []
    ga = np.pi * (3 - np.sqrt(5))
    naxes = int(np.sqrt(n)) + 1
    for i in range(naxes):
        z = 1 - 2 * (i + 0.5) / naxes
        rho = np.sqrt(max(0, 1 - z * z))
        phi = i * ga
        ax = np.array([rho * np.cos(phi), rho * np.sin(phi), z])
        for k in range(naxes):
            ang = 2 * np.pi * k / naxes
            c, s = np.cos(ang), np.sin(ang)
            K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
            rots.append(np.eye(3) + s * K + (1 - c) * (K @ K))
    return rots


def main(syscode):
    seed_els, seed_xyz = read_pdb(SEED)
    cat_syms, cat_xyz = extract_cation(seed_els, seed_xyz)
    cat_xyz = cat_xyz - cat_xyz.mean(0)  # center

    syms, xyz = read_inc("iface_%s.coord.inc" % syscode)
    slab = (np.arange(len(syms)) < 64)
    cation_old = (np.arange(len(syms)) >= 64) & (np.arange(len(syms)) < 147)
    env_mask = ~cation_old
    target_com = xyz[cation_old].mean(0)
    env = xyz[env_mask]
    rcat = np.array([RCOV[s] for s in cat_syms])
    renv = np.array([RCOV[s] for s in np.array(syms)[env_mask]])

    best = (-1e9, None)
    for R in rand_rotations(4000):
        p = cat_xyz @ R.T + target_com
        d = np.linalg.norm(p[:, None] - env[None], axis=2)
        clr = (d - (rcat[:, None] + renv[None])).min()  # clearance beyond covalent sum
        if clr > best[0]:
            best = (clr, p)
    print("%s: best orientation clearance beyond covalent-sum = %.2f A" % (syscode, best[0]))
    cat_pos = best[1]

    # reassemble: slab + intact cation + (everything after old cation = anion+network)
    out_syms = list(np.array(syms)[slab]) + list(cat_syms) + list(np.array(syms)[np.arange(len(syms)) >= 147])
    out_xyz = np.vstack([xyz[slab], cat_pos, xyz[np.arange(len(syms)) >= 147]])
    assert out_syms[147] == "Al", "Al must land at index 147, got %s" % out_syms[147]

    out = "iface_%s_intact.coord.inc" % syscode
    with open(out, "w") as f:
        f.write(CELL + "    &COORD\n")
        for s, (x, y, z) in zip(out_syms, out_xyz):
            f.write("      %-2s %14.6f %14.6f %14.6f\n" % (s, x, y, z))
        f.write("    &END COORD\n")
    # contact report
    n = len(out_xyz)
    d = np.linalg.norm(out_xyz[:, None] - out_xyz[None], axis=2) + np.eye(n) * 99
    bad = []
    for i in range(n):
        for j in range(i + 1, n):
            if i < 64 and j < 64: continue
            h = (out_syms[i] == "H") + (out_syms[j] == "H")
            lim = 0.75 if h == 2 else (0.95 if h == 1 else 1.30)  # true clashes only
            if d[i, j] < lim:
                bad.append("%s%d-%s%d %.2f" % (out_syms[i], i, out_syms[j], j, d[i, j]))
    print("  wrote %s (%d atoms); hard clashes: %s" % (out, n, bad if bad else "NONE"))


if __name__ == "__main__":
    main(sys.argv[1])
