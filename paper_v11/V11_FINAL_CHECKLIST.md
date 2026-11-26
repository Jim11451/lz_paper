# V11 checklist

`PAPER_V11_FINAL.pdf` — 17 pages — md5 `420117e1c6c756455af59e37f8e7ed64`.
Sources `paper/`, figures `figures/`, data `data/GRID_V10.csv` (470 rows, 381 excluded).

## Page-by-page (PDF inspected, not the sources)

| p | content | result |
|---|---|---|
| 1 | title, abstract | placeholder authors still present |
| 2 | §1, §2, Eq. (2) + κ² statement | corrected relation visible |
| 3 | Table 1, §3 opening | no overflow |
| 4 | §3.1–3.2, halo note, Eq. (5) | "We adopt" punctuation fixed |
| 5 | Eq. (6), §3.3, Fig. 1 | recalibrated (a)/(b) |
| 6 | §4.1–4.2 | binning paragraph rewritten |
| 7 | §4.3, §5.1 | Table 2 caption ok |
| 8 | Table 2 + Fig. 2 + §5.2 text | full page, no gap |
| 9 | §5.3 text + Fig. 3 + text | correct order |
| 10 | Fig. 4 + §6 start | full page |
| 11 | §6.1 | 470/470/471 counts, precision statement |
| 12 | Table 3 | caption now states what the resampling includes |
| 13 | §6.2–6.3, Table 4 | 468 corrected; κ row range |
| 14 | §7.1–7.2 | κ propagation text |
| 15 | §8 + Appendix A + Table 5 | note below tabular |
| 16 | Fig. 5 + Table 6 | Table 6 caption fixed |
| 17 | References | 14 entries |

## Numbers verified in the PDF

381 / 89 / 43; 0.00315; 1.0003, 1.0095, 1.0105; 1.077, 1.085, 0.800; 0.923±0.086, 0.863±0.080,
1.231±0.060, 1.229±0.062; 0.0365 → 0.0380/0.0422; 8–223 MeV, 39 MeV; 0.07%, 0.21%, 0.14%, 0.55%,
0.67%, 0.02%, 0.56%; 2.7, 3.0, 0.17, 0.89, 2×10⁻⁵; 9642.0, 10224, 3.198%; 0.0022–10.93;
8.3×10⁶; 1.38×10⁵; 0.66–6.59%; 1.2–8.4%; 132/338; 11 points for the κ shift.

## Code checks performed this round

* `step66_envelopes.py` — κ variation implemented as a flat signal factor (±10%). Wrong
  propagation; replaced by $\mathrm{BR_{inv}}$ propagation (see changelog item 12).
* `combine_50k.py` — 200 Poisson resamplings of the raw 15-bin histogram; includes the yield
  fluctuation; efficiency error excluded. Table 3 caption matches the code.
* `lz_recoil2.c` / `selfconsistent_scan_v2.py` — splitting fixed at $\Delta m=0.001$ GeV; used in
  the §5.2 wording.

## Deliberately unchanged

* 470 points, 381/89 classification, all μ95 values, the likelihood, the figures' underlying data
  (except the five repaired nodes already documented in V9/H_REPAIR).
* Nothing in `V7_EXTENSION/results`, `data/` or `V9_FINAL_REVIEW_REVISION` was modified.

## Still open

* Author list / affiliation.
* κ systematic propagated at fixed $m_\chi$ (stated in the caption); no joint re-solve.
* §6 window test remains a numerical statement, not a proof.
