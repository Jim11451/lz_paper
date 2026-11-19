# Archived audit notes for the parent PseudoDiracB UFO

This file describes the parent model.  The active flavor-EFT modifications are
documented in `FLAVOR_EFT_NOTES.md`.

This copy preserves the particle content and coupling magnitudes of the shared
`/home/cms/PseudoDiracB_UFO` snapshot dated 2026-10-05, while making the model
suitable for MadGraph parameter scans.

- `gB`, `gChi`, `dM`, `Mchi`, `MV`, `Wchi2`, and `WV` are external LHA
  parameters.
- A dedicated `PDB` interaction order is defined and used by both new
  vertices.
- The six `V-q-q` vertices use `Identity(1,2)` rather than the color-scalar
  string `1`.  This is required to contract the quark color indices and to
  generate ISR processes such as `pp > chi1 chi2 j` correctly.
- `WV` has a nonzero benchmark default (`7.0e-11 GeV`, the approximate
  quark width at the paper benchmark).  MadGraph removes an exactly-zero
  default width from generated propagator code, which prevents later width
  scans and produces an on-shell singularity.  The same nonzero value is set
  in `restrict_default.dat`, because MadGraph applies that restriction at
  import time.
- The quark-vector coupling includes the UFO vertex phase `i`, and the
  off-diagonal Majorana-vector coupling uses the sign obtained from
  `L_int = i gChi/2 V_mu bar(chi1) gamma^mu chi2`.

Benchmark defaults remain `Mchi=35 GeV`, `dM=0.001 GeV`, `MV=30 GeV`,
`gB=1.46e-5`, and `gChi=0.32`.
