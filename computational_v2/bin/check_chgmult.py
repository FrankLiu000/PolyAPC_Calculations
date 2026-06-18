#!/usr/bin/env python3
"""Verify charge/multiplicity of every G16 deck against electron parity and redox logic."""
import os, re, glob
Z = {'H':1,'C':6,'N':7,'O':8,'F':9,'Na':11,'Mg':12,'Al':13,'Si':14,'P':15,'S':16,'Cl':17}
RM = '/CH/poly_v2/run_mol'
ST = '/CH/poly_v2/common/struct'

spec = {}                                  # species -> (Zsum, native_charge)
for f in glob.glob(ST + '/*.xyz'):
    name = os.path.basename(f)[:-4]
    L = open(f).read().splitlines()
    try: nat = int(L[0])
    except Exception: continue
    m = re.search(r'charge\s*([+-]?\d+)', L[1] if len(L) > 1 else '')
    chg = int(m.group(1)) if m else 0
    zs = 0
    for ln in L[2:2+nat]:
        p = ln.split()
        if not p: continue
        el = p[0]
        el = el[0].upper() + el[1:].lower() if len(el) > 1 else el.upper()
        zs += Z.get(el, 0)
    spec[name] = (zs, chg)

names = sorted(spec, key=len, reverse=True)
def species_of(job):
    for s in names:
        if job == s or job.startswith(s + '_'):
            return s
    return None

issues, checked = [], 0
for g in sorted(glob.glob(RM + '/*.gjf')):
    job = os.path.basename(g)[:-4]
    s = species_of(job)
    if not s:
        issues.append((job, 'NO-SPECIES-MATCH')); continue
    zsum, nat = spec[s]
    cm = None
    for ln in open(g):
        p = ln.split()
        if len(p) == 2 and re.match(r'^-?\d+$', p[0]) and re.match(r'^\d+$', p[1]):
            cm = (int(p[0]), int(p[1])); break
    if cm is None:
        issues.append((job, 'NO-CHG/MULT-LINE')); continue
    chg, mult = cm
    elec = zsum - chg
    parity_ok = (elec % 2 == 0) == (mult % 2 == 1)
    r = job[len(s):]
    exp = nat + 1 if '_ox' in r else (nat - 1 if ('_red' in r or 'scan' in r) else nat)
    chg_ok = (chg == exp)
    checked += 1
    if not (parity_ok and chg_ok):
        issues.append((job, 'chg=%d mult=%d elec=%d parity_ok=%s exp_chg=%d chg_ok=%s'
                       % (chg, mult, elec, parity_ok, exp, chg_ok)))

print('species parsed: %d ; decks checked: %d ; ISSUES: %d' % (len(spec), checked, len(issues)))
for j, msg in issues:
    print('  %-34s %s' % (j, msg))
# also print the per-species parent table for eyeballing
print('\n--- species electron/charge table ---')
for s in sorted(spec):
    if any(os.path.exists(RM + '/' + s + suf + '.gjf') for suf in ('_opt', '_ramanopt')):
        zs, ch = spec[s]
        print('  %-26s Zsum=%4d native_charge=%+d  neutral_elec=%d' % (s, zs, ch, zs))
