#!/usr/bin/env bash
# scf_remedy.sh <jobname> — resubmit a "shaking" (SCF non-converged) G16 job with a
# hardened SCF and an altered initial guess, preserving the method/basis/chemistry:
#   * SCF -> scf=(xqc,maxcycle=512)   (quadratically-convergent fallback)
#   * open-shell (mult>1) -> add guess=mix (break spin symmetry); merge with guess=read
# The failing log is kept as <name>.log.shaking. Method/basis/charge/geometry unchanged.
set +u
RM=/CH/poly_v2/run_mol; BIN=/CH/poly_v2/bin
name="$1"; gjf="$RM/$name.gjf"
[ -f "$gjf" ] || { echo "scf_remedy: no $gjf"; exit 1; }
[ -f "$RM/$name.log" ] && mv -f "$RM/$name.log" "$RM/$name.log.shaking"

# multiplicity from the 'charge mult' line
mult=$(awk 'NF==2 && $1 ~ /^-?[0-9]+$/ && $2 ~ /^[0-9]+$/ {print $2; exit}' "$gjf")
mult=${mult:-1}

awk -v mult="$mult" '
  /^#/ && !done {
    line=$0
    gsub(/[Ss][Cc][Ff]=\([^)]*\)/,"",line); gsub(/[Ss][Cc][Ff]=[^ ]+/,"",line)
    line=line " scf=(xqc,maxcycle=512)"
    if (mult+0>1) {
      if (line ~ /[Gg][Uu][Ee][Ss][Ss]=\(/)      { sub(/[Gg][Uu][Ee][Ss][Ss]=\([^)]*\)/,"guess=(read,mix)",line) }
      else if (line ~ /[Gg][Uu][Ee][Ss][Ss]=read/){ sub(/[Gg][Uu][Ee][Ss][Ss]=read/,"guess=(read,mix)",line) }
      else                                        { line=line " guess=mix" }
    }
    gsub(/  +/," ",line); print line; done=1; next
  }
  { print }
' "$gjf" > "$gjf.tmp" && mv -f "$gjf.tmp" "$gjf"

ncores=$(awk -F= 'tolower($0) ~ /nprocshared/{print $2; exit}' "$gjf"); ncores=${ncores:-8}
jid=$(sbatch --parsable -c "$ncores" -D "$RM" "$BIN/run_g16.sh" "$name")
echo "scf_remedy: $name (mult=$mult) -> hardened scf=xqc$([ "$mult" -gt 1 ] && echo ' + guess=mix'); resubmitted jid=$jid"
