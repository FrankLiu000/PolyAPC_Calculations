#!/usr/bin/env python3
"""Validate the external-q*E field term against EPYC's biased DFT frames.
EPYC labels the SAME geometry at q=+1 and q=-1, so dF = F_dft(+1) - F_dft(-1)
isolates the pure bias response. The q*E model predicts dF_z(atom) = q_atom*dE
(single effective field step dE). We regress dF_z vs q_atom per system:
  high R^2 + small residual on the reducible Al  => q*E reproduces the EDL response (interim OK)
  large residual / bare!=poly slope             => electrode response dominates (need charge-aware model)
No MACE needed (the r6 baseline cancels in the +1/-1 difference).
usage: validate_qE.py
"""
import numpy as np
from ase.io import read

F = "incoming/biased_labeled.xyz".replace("incoming","../incoming") if False else "../incoming/biased_labeled.xyz"
frames = read(F, index=":")
qbare = np.load("t17/bare_start_charges.npy")
qpoly = np.load("t17/poly_start_charges.npy")

def get_F(at):
    f = at.arrays.get("forces")
    if f is None:
        try: f = at.get_forces()
        except Exception: f = None
    return np.array(f, float)

def netq(at):
    for k in ("net_charge","charge","total_charge"):
        if k in at.info:
            try: return float(at.info[k])
            except Exception: pass
    return None

# bucket frames by system, and pair +1/-1 by identical geometry
def geomkey(at): return np.round(at.get_positions(),3).tobytes()
buckets = {"bare":{}, "poly":{}}
for at in frames:
    ct = at.info.get("config_type","")
    sysn = "bare" if "bare" in ct else ("poly" if "poly" in ct else None)
    if sysn is None: continue
    q = netq(at)
    buckets[sysn].setdefault(geomkey(at), {})[round(q)] = at

for sysn, qarr in [("bare",qbare),("poly",qpoly)]:
    pairs = [(d[1], d[-1]) for d in buckets[sysn].values() if 1 in d and -1 in d]
    print(f"\n===== {sysn.upper()}  ({len(pairs)} matched +1/-1 geometry pairs) =====")
    if not pairs:
        print("  no paired geometries"); continue
    # verify atom-order matches the charge array on the first pair
    a0 = pairs[0][0]
    if len(a0) != len(qarr):
        print(f"  WARN natoms {len(a0)} != charges {len(qarr)}; skip"); continue
    allq=[]; alldFz=[]; alres=[]
    AlF_dft=[]; AlF_qE=[]
    # find Al index (reducible)
    Ali = [i for i,s in enumerate(a0.get_chemical_symbols()) if s=="Al"][0]
    for ap, am in pairs:
        dF = get_F(ap) - get_F(am)            # F(+1) - F(-1), the bias response
        allq.append(qarr); alldFz.append(dF[:,2])
    Q = np.concatenate(allq); DFZ = np.concatenate(alldFz)
    # least-squares slope dE through origin: dF_z ~ q * dE
    dE = float((Q@DFZ)/(Q@Q))
    pred = Q*dE
    ss_res = float(((DFZ-pred)**2).sum()); ss_tot = float((DFZ**2).sum())
    R2 = 1 - ss_res/ss_tot if ss_tot>0 else float("nan")
    mae_raw = float(np.abs(DFZ).mean()); mae_res = float(np.abs(DFZ-pred).mean())
    print(f"  q*E fit: effective dE={dE:+.3f} (V/A-equiv) | R^2={R2:.3f}  (1=q*E fully explains bias response)")
    print(f"  |dF_z| mean: raw={mae_raw:.3f} -> residual after q*E={mae_res:.3f} eV/A  (captured {100*(1-mae_res/mae_raw):.0f}%)")
    # reducible-Al specific
    for ap,am in pairs:
        dfal = (get_F(ap)-get_F(am))[Ali,2]
        AlF_dft.append(dfal); AlF_qE.append(qarr[Ali]*dE)
    AlF_dft=np.array(AlF_dft); AlF_qE=np.array(AlF_qE)
    print(f"  reducible Al (q_Al={qarr[Ali]:+.2f}): DFT bias response |dF_z|={np.abs(AlF_dft).mean():.3f}, "
          f"q*E predicts {np.abs(AlF_qE).mean():.3f}, residual(electrode resp)={np.abs(AlF_dft-AlF_qE).mean():.3f} eV/A")
