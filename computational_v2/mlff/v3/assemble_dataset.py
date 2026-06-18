#!/usr/bin/env python3
"""T16 dataset assembly: ingest EPYC's labeled frames (DATASET_SPEC.md) -> gated,
deduped, stratified train/val/test in extended-xyz for MACE.

Gate (the v2 lesson): slab-bottom forces must be MASKED (~0) -- else the +z
asymmetric-slab dipole artifact (‖ΣF‖~70-90 eV/Å) makes the set unfittable; and
energies must be single-points. We re-check ‖ΣF_slab‖≈0 and report ‖ΣF_total‖.

usage: assemble_dataset.py <incoming_dir> <out_dir> [val_frac] [test_frac]
"""
import sys, os, json, glob, hashlib
import numpy as np
from ase.io import read, write

inc, out = sys.argv[1], sys.argv[2]
val_frac = float(sys.argv[3]) if len(sys.argv) > 3 else 0.10
test_frac = float(sys.argv[4]) if len(sys.argv) > 4 else 0.10
os.makedirs(out, exist_ok=True)
SLAB_TOL = 0.5     # eV/Å : ‖ΣF_slab‖ must be below this (masked); else WARN
ELEM_OK = {"Mg","Al","Cl","O","C","H","Si"}

def geom_hash(at):
    return hashlib.md5(np.round(at.get_positions(),3).tobytes()).hexdigest()

def get_E(at):
    if "energy" in at.info: return float(at.info["energy"])
    try: return float(at.get_potential_energy())   # ASE routes energy= to a SinglePointCalculator on read
    except Exception: return np.nan

def get_F(at):
    F = at.arrays.get("forces")
    if F is None:
        try: F = at.get_forces()
        except Exception: F = None
    return F

frames=[]; report={}; seen=set(); dropped=0
for f in sorted(glob.glob(os.path.join(inc,"*.xyz"))):
    mask=None
    mj=f.replace(".xyz","_maskidx.json")
    if os.path.exists(mj): mask=set(json.load(open(mj)).get("masked",[]))
    try: ats=read(f,index=":")
    except Exception as e: print(f"  SKIP {f}: {e}"); continue
    for at in ats:
        ct = at.info.get("config_type","unknown")
        els = set(at.get_chemical_symbols())
        if not els <= ELEM_OK:
            print(f"  WARN {f}: unexpected elements {els-ELEM_OK}")
        h=geom_hash(at)
        if h in seen: dropped+=1; continue
        seen.add(h)
        F=get_F(at)
        if F is None: print(f"  WARN frame in {f} has no forces; skip"); dropped+=1; continue
        # slab mask: explicit indices, or comment n_slab_masked first-k, or config-type heuristic
        if mask is not None: midx=np.array(sorted(mask),dtype=int)
        elif "n_slab_masked" in at.info: midx=np.arange(int(at.info["n_slab_masked"]))
        else: midx=np.array([],dtype=int)
        sigF_slab = np.linalg.norm(F[midx].sum(0)) if len(midx) else 0.0
        emask=np.ones(len(at),bool);
        if len(midx): emask[midx]=False
        sigF_el = np.linalg.norm(F[emask].sum(0))
        rec=report.setdefault(ct, dict(n=0,emin=1e9,emax=-1e9,fmax=0,sigF_slab=[],sigF_el=[]))
        rec["n"]+=1; e=get_E(at)
        if np.isfinite(e): rec["emin"]=min(rec["emin"],e); rec["emax"]=max(rec["emax"],e)
        rec["fmax"]=max(rec["fmax"],float(np.abs(F[emask]).max()) if emask.any() else 0)
        rec["sigF_slab"].append(float(sigF_slab)); rec["sigF_el"].append(float(sigF_el))
        at.info.setdefault("config_type",ct)
        frames.append(at)
# stratified split by config_type
import random; rnd=random.Random(20260618)
by={}
for at in frames: by.setdefault(at.info.get("config_type","unknown"),[]).append(at)
train=[];val=[];test=[]
for ct,lst in by.items():
    rnd.shuffle(lst); n=len(lst); nt=int(n*test_frac); nv=int(n*val_frac)
    test+=lst[:nt]; val+=lst[nt:nt+nv]; train+=lst[nt+nv:]
for nm,lst in [("train",train),("val",val),("test",test)]:
    if lst: write(os.path.join(out,f"{nm}.xyz"),lst)
# E0 least-squares estimate (per element) from train energies
def e0_estimate(lst):
    if not lst: return {}
    els=sorted(ELEM_OK); A=[];b=[]
    for at in lst:
        c=[ (np.array(at.get_chemical_symbols())==e).sum() for e in els]; A.append(c); b.append(get_E(at))
    A=np.array(A,float); b=np.array(b,float)
    try: x,*_=np.linalg.lstsq(A,b,rcond=None); return {e:round(v,3) for e,v in zip(els,x)}
    except Exception: return {}

print("\n================ DATASET GATE REPORT ================")
print(f"incoming={inc}  unique frames={len(frames)}  dropped(dupes/no-F)={dropped}")
trainable=True
for ct,r in sorted(report.items()):
    ss=np.array(r["sigF_slab"]); se=np.array(r["sigF_el"])
    flag = "" if (ss.size==0 or ss.max()<SLAB_TOL) else f"  <-- ‖ΣF_slab‖ up to {ss.max():.1f} eV/Å NOT MASKED!"
    print(f"  {ct:18s} n={r['n']:4d}  E[{r['emin']:.1f},{r['emax']:.1f}]eV  |F_el|max={r['fmax']:.2f}  "
          f"ΣF_slab≈{ss.mean() if ss.size else 0:.3f}  ΣF_el≈{se.mean() if se.size else 0:.3f}{flag}")
    if flag: trainable=False
need_bare = report.get("t10_react_bare",{}).get("n",0)
need_poly = report.get("t10_react_poly",{}).get("n",0)
print(f"\nsplit -> train={len(train)} val={len(val)} test={len(test)}  ({out}/)")
print(f"E0 estimate (train): {e0_estimate(train)}")
print(f"T10 coverage: bare={need_bare} poly={need_poly} (spec wants >=300 each)")
ok = trainable and need_bare>=300 and need_poly>=300
print(f"\n==> {'TRAINABLE' if ok else 'NOT YET TRAINABLE'} "
      f"({'masking OK + T10 sufficient' if ok else 'fix masking and/or wait for more T10 frames'})")
json.dump({k:{kk:(vv if not isinstance(vv,list) else [round(x,3) for x in vv]) for kk,vv in v.items()} for k,v in report.items()},
          open(os.path.join(out,"gate_report.json"),"w"), indent=2)
