#!/usr/bin/env python3
"""fix_iface_coords.py — repair the corrupted interface starting geometries.

Bug (both systems): the cation's 3 bridging Cl (atoms 66,67,68 0-based) were all
placed at the SAME mu-bridge site between Mg64/Mg65 (Cl-Cl 1.23/1.33 A) instead of
120 deg apart around the Mg-Mg axis -> explosive start (T spike >1000 K, HCl ejection,
spurious chloride scattering). Poly extra: H269/H270 on C245 collapsed (0.68 A).

Fix: place the 3 Cl at d(Cl-Mg)=2.50 A to both Mg (radius about the Mg-Mg midpoint),
azimuth chosen by scanning 0..120 deg for the max-min clearance to all other atoms;
rebuild the two H on C245 with ideal sp3 geometry. Writes <stem>_v2.coord.inc.
"""
import numpy as np
import sys

D_CLMG = 2.50
CH = 1.09


def read_inc(path):
    pre, atoms, post, inblk, done = [], [], [], False, False
    for l in open(path):
        s = l.strip()
        if s.startswith("&COORD"):
            inblk = True; pre.append(l); continue
        if s.startswith("&END COORD"):
            inblk = False; done = True; post.append(l); continue
        if inblk:
            atoms.append(l)
        elif not done:
            pre.append(l)
        else:
            post.append(l)
    syms = [a.split()[0] for a in atoms]
    xyz = np.array([[float(v) for v in a.split()[1:4]] for a in atoms])
    return pre, syms, xyz, post


def place_bridging_cl(syms, xyz):
    m1, m2 = xyz[64], xyz[65]
    mid, u = 0.5 * (m1 + m2), (m2 - m1) / np.linalg.norm(m2 - m1)
    half = 0.5 * np.linalg.norm(m2 - m1)
    r = np.sqrt(D_CLMG**2 - half**2)
    v1 = np.cross(u, [0.0, 0.0, 1.0]); v1 /= np.linalg.norm(v1)
    v2 = np.cross(u, v1)
    others = np.array([x for i, x in enumerate(xyz) if i not in (64, 65, 66, 67, 68)])
    best = (-1.0, None)
    for th0 in np.radians(np.arange(0, 120, 2)):
        cls = [mid + r * (np.cos(th0 + k) * v1 + np.sin(th0 + k) * v2)
               for k in (0.0, 2.0944, 4.18879)]
        clear = min(np.linalg.norm(others - c, axis=1).min() for c in cls)
        if clear > best[0]:
            best = (clear, cls)
    print("  Cl placement: min clearance to rest of system %.2f A" % best[0])
    for c, idx in zip(best[1], (66, 67, 68)):
        xyz[idx] = c
    return xyz


def fix_ch2(syms, xyz, h=(269, 270)):
    """Split the collapsed H pair (0.68 A apart) to a normal H-C-H opening.
    Defensive: works off whatever carbon they share; GEO_OPT then relaxes exact angles."""
    c = int(np.argmin([np.linalg.norm(xyz[i] - xyz[h[0]]) if syms[i] == "C" else 9e9
                       for i in range(len(xyz))]))
    print("  CH2 fix: H%d/H%d share C%d (d %.2f A apart)"
          % (h[0], h[1], c, np.linalg.norm(xyz[h[0]] - xyz[h[1]])))
    mid = 0.5 * (xyz[h[0]] + xyz[h[1]])
    b = mid - xyz[c]; b /= np.linalg.norm(b)            # C -> H bisector
    p = np.cross(b, [0.0, 0.0, 1.0]); p /= np.linalg.norm(p)  # in-plane perpendicular
    ang = np.radians(109.47 / 2)
    xyz[h[0]] = xyz[c] + CH * (np.cos(ang) * b + np.sin(ang) * p)
    xyz[h[1]] = xyz[c] + CH * (np.cos(ang) * b - np.sin(ang) * p)
    return xyz


def contact_scan(syms, xyz, label):
    n = len(xyz)
    d = np.linalg.norm(xyz[:, None, :] - xyz[None, :, :], axis=2) + np.eye(n) * 99
    iu = np.triu_indices(n, 1)
    worst = []
    for i, j in zip(*iu):
        hyd = (syms[i] == "H") + (syms[j] == "H")
        lim = 0.85 if hyd == 2 else (0.95 if hyd == 1 else 1.75)
        pair = {syms[i], syms[j]}
        if pair <= {"C", "O", "Si"} or pair == {"C"}: lim = 1.3
        if d[i, j] < lim:
            worst.append("%s%d-%s%d %.2f" % (syms[i], i, syms[j], j, d[i, j]))
    print("  %s contact scan: %s" % (label, worst if worst else "CLEAN"))
    return not worst


def main(path, out, poly):
    pre, syms, xyz, post = read_inc(path)
    print(path, "->", out)
    xyz = place_bridging_cl(syms, xyz)
    if poly:
        xyz = fix_ch2(syms, xyz)
    ok = contact_scan(syms, xyz, "fixed")
    with open(out, "w") as f:
        f.writelines(pre)
        for s, (x, y, z) in zip(syms, xyz):
            f.write("      %-2s %14.6f %14.6f %14.6f\n" % (s, x, y, z))
        f.writelines(post)
    return ok


if __name__ == "__main__":
    ok1 = main("iface_bare.coord.inc", "iface_bare_v2.coord.inc", poly=False)
    ok2 = main("iface_poly.coord.inc", "iface_poly_v2.coord.inc", poly=True)
    sys.exit(0 if (ok1 and ok2) else 1)
