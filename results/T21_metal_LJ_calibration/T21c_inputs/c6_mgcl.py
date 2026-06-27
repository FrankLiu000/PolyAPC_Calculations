#!/usr/bin/env python3
# C6 -> LJ for Mg-X, same protocol as C/Si/S pairs (D3 E_disp at r=5.0 A, damping~1).
BOHR = 0.5291772            # A per Bohr
HA2KJ = 2625.499            # kJ/mol per Hartree
A2NM = 0.1                  # nm per A
r_A = 5.0
r_bohr = r_A / BOHR
sig_Mg = 0.29436            # nm (my metal LJ)
sig_X = {'S': 0.355, 'C': 0.355, 'Si': 0.392, 'Cl': 0.340}  # OPLS elemental sigma (nm)
Edisp = {'S': -0.000396, 'Cl': -0.00036535142441}           # Ha at 5 A

def lj(el, E):
    C6_au = -E * r_bohr**6
    # C6 in kJ/mol * nm^6 : au(Ha*Bohr^6) -> Ha->kJ/mol, Bohr->nm
    C6_kjnm6 = C6_au * HA2KJ * (BOHR*A2NM)**6
    sig = (sig_Mg * sig_X[el])**0.5
    eps = C6_kjnm6 / (4.0 * sig**6)
    return sig, eps, C6_au

for el in ['S', 'Cl']:
    sig, eps, C6 = lj(el, Edisp[el])
    print(f"Mg-{el}: C6_au={C6:8.2f}  sigma={sig:.5f} nm  eps={eps:.3f} kJ/mol")
print("(Mg-S check should ~match the committed 0.32326/3.556)")
