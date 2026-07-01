# T23 Publication Gate Status

Generated from live CP2K outputs by `hpc/t23/monitor_t23_milestones.py`.

This file is a conservative guardrail: early fs-scale contact is useful running evidence, but it is not a manuscript-level AIMD claim until the replicate and length gates pass.

## Gates

- Interim event gate: at least one bare contact-release seed with >= 500 fs sustained slab-contact + low-qAl.
- Near-contact watch gate: at least one bare contact-release seed with >= 500 fs sustained near-contact (Al-slab <= 3.0 A) + low-qAl. This is a monitoring aid, not a replacement for the strict gate.
- Dechlorination watch gate: at least one bare contact-release seed with >= 500 fs sustained near-contact + low-qAl + nCl<=1. This is a co-deposition-supporting diagnostic, not a replacement for the strict gate.
- Publication bare gate: three bare contact-release seeds with >= 3000 fs trajectory length and >= 3000 fs sustained slab-contact + low-qAl.
- Publication poly-control gate: three poly z032 close-approach negative controls with >= 3000 fs trajectory length and <= 100 fs sustained slab-contact + low-qAl. These are not forced T23b contact-frame analogues; forcing Al through the POSS network would overstate physical sampling.

## Current Verdict

- interim_0p5ps_event: False
- interim_0p5ps_near_event: True
- interim_0p5ps_near_dechlorinated_event: True
- bare_publication_replicates: False
- poly_publication_negative_controls: False
- publication_ready: False

## Counts

| item | count |
|---|---:|
| bare_contact_release_total | 3 |
| bare_contact_release_started | 2 |
| bare_contact_release_interim_event_seeds | 0 |
| bare_contact_release_interim_near_event_seeds | 2 |
| bare_contact_release_interim_near_dechlorinated_event_seeds | 1 |
| bare_contact_release_publication_seeds | 0 |
| poly_negative_control_total | 3 |
| poly_negative_control_started | 0 |
| poly_negative_control_publication_seeds | 0 |

## Bare Contact-Release Seeds

| project | last energy fs | last geom fs | strict longest fs | strict current fs | near longest fs | near current fs | near+nCl<=1 longest fs | near+nCl<=1 current fs | MgCoord longest fs | MgCoord current fs | last nMg<=3.2 | last Al height (A) | last Al-slab (A) | last qAl |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| t23b_codep_contact_release_bare_qm2_s1_300K | 1787.0 | 1785.0 | 240.0 | 55.0 | 915.0 | 320.0 | 740.0 | 320.0 | 1785.0 | 1785.0 | 1 | 2.572 | 2.784 | 0.1817 |
| t23b_codep_contact_release_bare_qm2_s2_325K | 847.5 | 845.0 | 200.0 | 0.0 | 720.0 | 720.0 | 475.0 | 475.0 | 720.0 | 720.0 | 1 | 2.717 | 2.829 | 0.2107 |
| t23b_codep_contact_release_bare_qm2_s3_350K | NA | NA | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | NA | NA | NA |

## Poly Negative Controls

| project | last energy fs | last geom fs | strict longest fs | strict current fs | near longest fs | near current fs | near+nCl<=1 longest fs | near+nCl<=1 current fs | MgCoord longest fs | MgCoord current fs | last nMg<=3.2 | last Al height (A) | last Al-slab (A) | last qAl |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| t23_release_poly_qm2_s1_300K | NA | NA | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | NA | NA | NA |
| t23_release_poly_qm2_s2_325K | NA | NA | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | NA | NA | NA |
| t23_release_poly_qm2_s3_350K | NA | NA | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | NA | NA | NA |
