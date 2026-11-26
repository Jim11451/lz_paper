# Review pack — Fig. 2 colour step (20 → 30 GeV) and the 25 GeV curve in Fig. 3

Two questions for the reviewer:

1. Is the abrupt colour change between the $M_V=20$ and $M_V=30$ GeV columns of Fig. 2
   explained correctly, or is it a plotting artefact?
2. Is it acceptable to add an **interpolated** $M_V=25$ GeV curve to Fig. 3, labelled as such,
   when no 25 GeV solutions exist in the grid?

## The claim under review

**Fig. 2.** Cells are coloured by $\log_{10}\mu_{95}$ with a two-slope normalisation
($\mu_{95}=1$ at the neutral tone; the scale spans $3.2\times10^{-3}$ to $64$). Cell edges sit at
the logarithmic midpoints between neighbouring coupling values and at the midpoints between
columns, so no colour is interpolated. The 20 → 30 GeV step is therefore drawn as a hard edge,
but the change is physical:

| $M_V$ | points | excluded | median $\mu_{95}$ | $\mu_{95}$ range | median $\mathrm{BR_{inv}}$ |
|---|---|---|---|---|---|
| 20 | 44 | 1 | 3.66 | 0.94 – 64 (cap) | 0.018 |
| 30 | 44 | 34 | 0.405 | 0.099 – 2.93 | 0.580 |

At matched $g_t$ the dark coupling is about a factor 9.5 larger in the 30 GeV column, because
$g_\chi=\kappa(m_\chi)M_V^2/g_t$ and both $\kappa$ and $M_V^2$ grow with the column:

| $g_t$ | $g_\chi$ (20 GeV) | $g_\chi$ (30 GeV) | $\mathrm{BR_{inv}}$ 20 / 30 | $\mu_{95}$ 20 / 30 |
|---|---|---|---|---|
| 0.1514 | 0.032 | 0.307 | 0.804 / 0.997 | 1.181 / 1.077 |
| 0.1788 | 0.027 | 0.257 | 0.677 / 0.995 | 1.000 / 0.657 |
| 0.1942 | 0.024 | 0.235 | 0.600 / 0.993 | 1.333 / 0.671 |
| 0.2941 | 0.016 | 0.150 | 0.224 / 0.962 | 1.746 / 0.321 |

So at 20 GeV the mediator decays mostly to quarks already at $g_t\approx0.23$
($\mathrm{BR_{inv}}<0.5$), the invisible signal collapses, and almost the whole column survives
(the median $\mu_{95}$ sits a factor 9 above the 30 GeV value, and many points hit the
$\mu_{95}=64$ cap). At 30 GeV the invisible channel stays open to $g_t\approx0.67$, the signal is
present across the column and 34 of 44 points are excluded.

The plotted step therefore reflects a real change of regime between the two columns; the only
graphical contribution is that the boundary is drawn at the midpoint (25 GeV) with no
interpolation, which is the stated construction.

**Fig. 3.** The grid has columns at 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180,
200 GeV — there is no 25 GeV column. The added curve is
$\mu_{95}(25)=\sqrt{\mu_{95}(20)\,\mu_{95}(30)}$ at fixed $g_t$ (logarithmic interpolation in
$M_V$), drawn dashed, labelled "interpolated", and named as such in the caption. It is not a
computed result and is not quoted in the text.

## Files

| file | what |
|---|---|
| `fig2_v10.pdf/.png` | the exclusion map |
| `fig3_v10.pdf/.png` | $\mu_{95}(g_t)$ with the interpolated 25 GeV curve |
| `column_stats.csv` | per-column counts, medians, $\mathrm{BR_{inv}}$, $2m_\chi/M_V$ |
| `GRID_V10.csv` | the 470-point grid (inputs to both figures) |
| `make_fig2_v10.py`, `make_figs_v10.py` | the plotting scripts |

## What the reviewer should check

1. Whether the mechanism above is right, in particular the claim that $g_\chi$ grows by ~9.5
   between columns at fixed $g_t$ and that this (not a change of $2m_\chi/M_V$, which is 0.86 vs
   0.84) is what keeps $\mathrm{BR_{inv}}\simeq1$ at 30 GeV.
2. Whether the hard cell edge at 25 GeV is defensible given that the paper states no colour is
   interpolated.
3. Whether an interpolated 25 GeV curve belongs in a published figure at all, and if so whether
   the labelling is sufficient.
4. Any inconsistency between these numbers and the text of Section 5.3.
