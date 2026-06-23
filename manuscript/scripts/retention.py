# -*- coding: utf-8 -*-
import csv, json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = r"C:/Users/刘悦铮/AppData/Local/Temp/claude/D--20260602-polyAPC-data/302d1e65-667d-4649-a77b-21f3a1304446/scratchpad/mo6s8_out"
FORM = 4   # formation cycles 1..4; reversible from cycle 5

def load(name):
    rows=[]
    with open(os.path.join(OUT,f"percycle_{name}.csv"),encoding="utf-8") as f:
        for x in csv.DictReader(f):
            rows.append((int(x["cycle"]),float(x["dis_spec_mAhg"]),float(x["chg_spec_mAhg"]),float(x["CE_pct"])))
    return rows

def analyze(name):
    rows=load(name)
    rev=[(c,ds,cs,ce) for (c,ds,cs,ce) in rows if c>FORM and ds>0]
    _e=max(rev,key=lambda x:x[1]); refc,refcap=_e[0],_e[1]   # max reversible discharge cap (ref)
    # 80% sustained crossing (2 consecutive cycles below)
    thr=0.8*refcap
    cross=None; below=0
    for (c,ds,cs,ce) in rev:
        if c<refc: continue
        if ds<thr:
            below+=1
            if below>=2: cross=c-1+1; break  # first cycle that went below (sustained)
        else: below=0
    # CE over >80% window
    win=[(c,ds,cs,ce) for (c,ds,cs,ce) in rev if (cross is None or c<=cross)]
    ces=[ce for (c,ds,cs,ce) in win if 95<=ce<=101]
    info=dict(name=name, last_cycle=rows[-1][0], formation_cycles=FORM,
              ref_cycle=refc, ref_cap_mAhg=round(refcap,2), thr80_mAhg=round(thr,2),
              cyc_at_80pct=cross,
              cap_first_rev_mAhg=round(rev[0][1],2),
              cap_last_mAhg=round(rows[-1][1],2),
              CE_mean_in_window_pct=round(sum(ces)/len(ces),2) if ces else None,
              n_in_window=len(win))
    # retention at milestones
    cap={c:ds for (c,ds,cs,ce) in rev}
    info["retention_at"]={}
    for mc in [100,200,500,800,1000,1300,1500,1600,1700,2000,2500,3000]:
        if mc in cap: info["retention_at"][mc]=round(cap[mc]/refcap*100,1)
    return rows,info

res={}; data={}
for n in ["poly_1C","poly_0p5C","bare_0p5C"]:
    data[n],res[n]=analyze(n)
    print(json.dumps(res[n],ensure_ascii=False,indent=2))
json.dump(res,open(os.path.join(OUT,"retention_summary.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=2)

# ---------- Figure: capacity + CE vs cycle ----------
fig,axes=plt.subplots(1,2,figsize=(11,4.2))
COL={"poly_1C":"#c0392b","poly_0p5C":"#2471a3","bare_0p5C":"#7f8c8d"}
LAB={"poly_1C":"poly-APC, 1C","poly_0p5C":"poly-APC, 0.5C","bare_0p5C":"bare-APC, 0.5C"}

# left: 0.5C poly vs bare (full)
ax=axes[0]
for n in ["poly_0p5C","bare_0p5C"]:
    rows=data[n]; refc=res[n]["ref_cycle"]; ref=res[n]["ref_cap_mAhg"]
    c=[x[0] for x in rows]; d=[x[1] for x in rows]
    ax.plot(c,d,color=COL[n],lw=1.3,label=LAB[n])
ax.set_xlabel("Cycle number"); ax.set_ylabel("Discharge capacity (mAh g$^{-1}$)")
ax.set_title("(a) 0.5C: poly stable vs bare death",fontsize=10)
ax.set_xlim(0,900); ax.set_ylim(0,105); ax.legend(fontsize=8,frameon=False)
ax.axhline(0.8*res["poly_0p5C"]["ref_cap_mAhg"],ls=":",color="#2471a3",lw=0.8)
ax.axhline(0.8*res["bare_0p5C"]["ref_cap_mAhg"],ls=":",color="#7f8c8d",lw=0.8)

# right: poly 1C truncated to >80% window (~1600) + CE on twin axis
ax=axes[1]
n="poly_1C"; rows=data[n]; cross=res[n]["cyc_at_80pct"]; ref=res[n]["ref_cap_mAhg"]
cutoff=cross if cross else rows[-1][0]
sel=[x for x in rows if x[0]<=cutoff]
c=[x[0] for x in sel]; d=[x[1] for x in sel]; ce=[x[3] for x in sel if x[3] is not None]
ax.plot(c,d,color=COL[n],lw=1.2,label=f"poly-APC 1C (cap)")
ax.axhline(0.8*ref,ls=":",color="#c0392b",lw=0.9)
ax.axvline(cross,ls="--",color="k",lw=0.8)
ax.text(cross,8,f" 80% @ cyc {cross}",fontsize=8)
ax.set_xlabel("Cycle number"); ax.set_ylabel("Discharge capacity (mAh g$^{-1}$)",color=COL[n])
ax.set_title("(b) 1C poly: capacity-retention >80% window",fontsize=10)
ax.set_ylim(0,105); ax.set_xlim(0,cutoff*1.05)
ax2=ax.twinx()
cc=[x[0] for x in sel]; cce=[x[3] for x in sel]
ax2.scatter(cc,cce,s=2,color="#27ae60",alpha=0.5)
ax2.set_ylabel("Coulombic efficiency (%)",color="#27ae60"); ax2.set_ylim(90,105)
plt.tight_layout()
fig.savefig(os.path.join(OUT,"fig_Mo6S8_cycling.png"),dpi=200)
print("FIG saved")
