# tt̄ + MET analysis — v2 (corrected κ) reproducibility package

This directory is the **v2 snapshot** of the tt̄+MET analysis, superseding the
κ used in `reproducibility/ttbar/` and in the early paper draft.

Two corrections define v2:

1. **κ<sub>LZ</sub> corrected.** The LZ normalisation now targets
   `N_ROI = 1.12044` events with `g_chi^lim = sqrt(N_target / N_ref)` and
   `κ = g_chi^lim / M_V,ref^2` (`M_V,ref = 100 GeV`), after fixing the
   `gB = 2 f_N` mapping and the `f_n/f_p` isotope weighting in the recoil code.
   The 36-node table closes against the reference values at the 0.1 % level
   (mean ratio 1.0005 over eight mass points).
2. **`g_t = 1` is no longer assumed.** The exclusion grid scans 44 values of
   `g_t` in `[0.1, sqrt(4π)]`, and each point carries its own
   `g_chi = κ(m_chi) M_V^2 / g_t` (verified to 2 × 10⁻¹⁶ against the grid file),
   its own `Γ_V`, and its own `BR_inv`.

## Quick verification (no external software)

```bash
python3 run.py --check     # sha256 of every shipped file against manifest.json
python3 run.py --widths    # re-derive widths_v2.csv from band_v2.csv
```

`--widths` compares the analytic partial widths with the frozen table:
`max |ΔΓ/Γ| = 3.4 × 10⁻⁶`, `max |ΔBR| = 5 × 10⁻⁷` (the latter is the 6-decimal
rounding of the stored column). Both checks pass with the standard library only.

## What each step needs

| Step | Script | Needs |
|---|---|---|
| κ(m_chi) — 36 nodes | `code/kappa_from_lz2.py` | micrOMEGAs tree with the modified `lz_recoil2` driver |
| relic band — 70 + 126 points | `code/solve_band_v2.py`, `code/extend_band.py` | micrOMEGAs 7.1.x, ~1 s/point |
| widths / BR | `code/widths_v2.py` (or `run.py --widths`) | pure Python |
| width cross-check vs micrOMEGAs | `code/validate_widths.py` | micrOMEGAs build with `width_drv` |
| exclusion grid — 616 points | `code/map_v2.py` | 14 Delphes samples (249 GB, not shipped), HEPData tables, `final_plot.shape()` |
| figures | `code/plots_v2.py` | `grid_v2.npz` (shipped) |
| 19-channel fit (Phase 12) | `reproducibility/ttbar/code/fit_cr.py` | pyhf 0.7.6 + iminuit |

Scripts keep the absolute paths of the original working tree; the packaged
inputs are meant for inspection and for the two checks above.

## Contents

```
inputs/    kappa_lz_gN_v2.csv (36)  band_v2.csv (70)  band_v2_ext.csv (126)
           band_v2_validity2/3.csv  widths_v2.csv (70)  sigma_MV.csv (14)
           grid_v2.csv / .npz (616) shapes_v2.npz
results/   fig_exclusion_v2.png  fig_boundary_eff.png
code/      kappa_from_lz2.py  solve_band_v2.py  widths_v2.py  extend_band.py
           validate_widths.py  map_v2.py  plots_v2.py  recompute2.py
           sys_likelihood.py  final_plot.py
docs/      STEP52_REPORT  STEP53_REPORT  STEP53_CHECKS  STEP54_FINAL_REPORT
           STEP541_WIDTH_VALIDATION  STEP55_AUDIT  PHASE12_AUDIT
           PHASE12_RERUN_REPORT  SIGNAL_REPRO_ALL_POINTS  RESEARCH_LOGIC_AUDIT
```

## Status of the grid

`grid_v2.csv` has 616 points: **244 physically valid** (183 excluded, 61
allowed), 372 invalid, each with the reason recorded in the `status` column.
The exclusion figure uses the single-region (AH 0ℓ2b, 15-bin) likelihood;
it is **not** the same statistical object as the 19-channel fit quoted in
`docs/PHASE12_*.md` — see `docs/RESEARCH_LOGIC_AUDIT.md` §2 for the
distinction that must be kept in the paper.
