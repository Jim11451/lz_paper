# V11 manuscript — exothermic pseudo-Dirac dark matter, $t\bar t$+MET constraints

LaTeX sources, figures, grid and compiled PDF for the V11 paper
(*Xenon recoils, Planck abundance and $t\bar t$+MET constraints on exothermic pseudo-Dirac dark matter*).

## Build

```bash
cd paper_v11
pdflatex main.tex
pdflatex main.tex        # second pass for references
```

17 pages, `PAPER_V11_FINAL.pdf` (md5 `bbeca9f5b0c6178c25cd54c2318a1b02`).
Figures are shipped as PDFs; they were produced from `data/GRID_V10.csv` by
`make_figs_v10.py` / `make_fig2_v10.py` in the analysis workspace
(`/home/yy/lz-event/phenomenology/V10_FINAL_MANUSCRIPT/code`), not included here.

## Contents

| path | what |
|---|---|
| `main.tex`, `sections/` | manuscript source (abstract, 8 sections, appendix, references) |
| `figs/` | Figs. 1–4 (self-made) and Fig. 5 (CMS published figure, external input) |
| `data/GRID_V10.csv` | the 470-point grid: $M_V$, $g_t$, $m_\chi$, $g_\chi$, $\Gamma_V$, $\mathrm{BR_{inv}}$, $\kappa$, $\mu_{95}$ |
| `V11_CHANGELOG.md` | what changed from V10, item by item |
| `V11_FINAL_CHECKLIST.md` | page-by-page and numerical checks |

## Data provenance and checks

`GRID_V10.csv` is a copy of `SELFCONSISTENT_MU95.csv` (470 rows) with the five nodes
2082, 2088, 2086, 1004, 1006 replaced by their re-solved values (converged relic solutions;
same classification). Recomputed from the shipped file:

* 470 rows, **381 excluded**, **89 surviving**, 43 of them at $M_V=20$ GeV (1 of 44);
* $\mu_{95}$ from 0.00315 to the cap 64.0;
* per-column counts 44/44/44/44/44/44/43/38/34/27/22/17/14/11, matching Table 2.

Event samples are **not** in this repository; the limits are reproduced from the frozen
templates and the published CMS post-fit distribution, as stated in the paper.

## Known limitations (as stated in the paper)

Expected-only recast; single signal region ($0\ell2b$); parameterised detector; fifteen
$p_T^{\rm miss}$ bins; on-shell branch only; $M_V\in[20,200]$ GeV; $m_\chi\le47.8$ GeV by
choice of grid; the $2\sigma$ robustness test covers the 132 points at 20–40 GeV only.

## Authors

Title page still carries a placeholder author list and affiliation; fill before submission.
