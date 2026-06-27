#!/usr/bin/env python3
# Quantify Mg-O: two-body potential (from the periodic slab+THF scan) + dG_ads(liquid) cycle.
import numpy as np
HA2EV=27.211386; HA2KJ=2625.499; EV2KJ=96.485
# *** TZVPP (TZV2P-MOLOPT-PBE-GTH) single-points -- REPLACES the earlier DZVP scan (2026-06-27) ***
E_slab=-2278.390738814; E_THF=-43.519160708; ref=E_slab+E_THF   # TZVPP fragments (tz_slab, tz_THF)
# slab+THF scan: z(A) -> total E(Ha), TZVPP (tz_sTHF_*).  [DZVP min was -0.675 eV @2.2 for comparison]
scan={1.8:-2321.913662718, 2.0:-2321.932197103, 2.2:-2321.936507681, 2.5:-2321.934031042,
      3.0:-2321.926446286, 3.5:-2321.920767141, 4.0:-2321.917020243, 5.0:-2321.913168357}
z=np.array(sorted(scan)); Eb=np.array([ (scan[k]-ref)*HA2EV for k in z ])  # eV
print("=== two-body Mg-O surface binding curve (vacuum, TZVPP raw) ===")
for zi,ei in zip(z,Eb): print(f"  z={zi:.1f} A   E_bind={ei:+.3f} eV")
imin=int(np.argmin(Eb));
# parabola fit near min (3 pts around minimum)
sel=[i for i in (imin-1,imin,imin+1) if 0<=i<len(z)]
a,b,c=np.polyfit(z[sel],Eb[sel],2)
z0=-b/(2*a); Emin=a*z0**2+b*z0+c
k_evA2=2*a; k_Nm=k_evA2*16.0218                      # eV/A^2 -> N/m
mu=72.107*1.66054e-27                                # THF mass (kg), rigid molecule vs fixed slab
nu_Hz=(1/(2*np.pi))*np.sqrt(k_Nm/mu); nu_cm=nu_Hz/2.998e10
print(f"\n  well: depth {Emin:.3f} eV at z0={z0:.2f} A ; curvature {k_evA2:.2f} eV/A^2 = {k_Nm:.1f} N/m")
print(f"  frustrated perpendicular (Mg-O stretch, rigid THF): nu ~ {nu_cm:.0f} cm^-1")
Vwell=-Emin
# counterpoise BSSE at the well z=2.2 (TZVPP ghost runs): E_int(CP)=E_dimer - E_slab(ghostTHF) - E_THF(ghostslab)
E_dim22=-2321.936507681; E_slab_gT=-2278.392071751; E_THF_gS=-43.519883466
V_raw22=(E_dim22-ref)*HA2EV; V_bsse=(E_dim22-E_slab_gT-E_THF_gS)*HA2EV
print(f"  raw TZVPP well {Emin:.3f} eV ; BSSE-corrected (counterpoise @2.2) {V_bsse:.3f} eV  (BSSE {V_raw22-V_bsse:+.3f} eV)")
print(f"  => TWO-BODY POTENTIAL (BSSE) |V| = {-V_bsse:.3f} eV ({-V_bsse*EV2KJ:.0f} kJ/mol)  [the explicit-liquid LJ pair anchor; eps 53.2]")

print("\n=== dG_ads(liquid THF) thermodynamic cycle ===")
dEbind=-0.668                                         # eV, TZVPP+BSSE vacuum surface binding (gold-std)
Sgas=302.4                                            # J/mol/K, THF gas standard entropy (NIST; cross-checked by g16 freq)
R=8.314; T=298.15
Sads=0.70*Sgas-3.3*R                                  # Campbell-Sellers empirical adsorbate entropy
mTdS=T*(Sgas-Sads)/1000.0                             # kJ/mol (positive = entropy penalty)
dGvap=+3.7                                            # kJ/mol, THF liquid->gas free energy (vapor pressure 298K)
dGads_gas=dEbind*EV2KJ + mTdS                         # gas-phase adsorption free energy (ZPE/thermal ~ small, omitted)
dGads_liq=dGads_gas + dGvap
print(f"  dE_bind(vac, TZVPP+BSSE) = {dEbind:+.3f} eV = {dEbind*EV2KJ:+.1f} kJ/mol")
print(f"  S_gas={Sgas:.0f}  S_ads(Campbell-Sellers)={Sads:.0f} J/mol/K  ->  -TdS = +{mTdS:.1f} kJ/mol")
print(f"  dG_vap(THF,298K) = +{dGvap:.1f} kJ/mol")
print(f"  dG_ads(gas->ads) = {dGads_gas:+.1f} kJ/mol")
print(f"  dG_ads(LIQUID)   = {dGads_liq:+.1f} kJ/mol  = {dGads_liq/EV2KJ:+.3f} eV   [EMERGENT PMF target]")

print("\n=== kinetic check: residence vs effective barrier (anchor to GPU's 90%-no-desorb/12ns@400K) ===")
for Ea in (0.26,0.40,0.55,0.67):
    for Tk in (298,400):
        kT=8.617e-5*Tk; tau_ps=np.exp(Ea/kT)         # tau0~1ps prefactor
        unit="ns" if tau_ps<1e6 else "us"; val=tau_ps/1e3 if tau_ps<1e6 else tau_ps/1e6
        print(f"  barrier {Ea:.2f} eV @ {Tk}K -> tau ~ {val:.2g} {unit}")
    print()
