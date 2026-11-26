# Review pack — Fig. 2 colour step (20 → 30 GeV) and the 25 GeV question

Two questions:

1. Is the abrupt colour change between the $M_V=20$ and $M_V=30$ GeV columns of Fig. 2
   physical, and is the explanation correct?
2. Should an interpolated $M_V=25$ GeV curve be added to Fig. 3 when no 25 GeV solutions exist?

**Status:** reviewed 2026-11-26. The mechanism in Q1 was confirmed and strengthened; the
interpolated curve in Q2 was rejected and has been removed. See "Changes made in response".

## 1. The claim under review

**Fig. 2 construction.** Cells are coloured by $\log_{10}\mu_{95}$ with a two-slope normalisation
($\mu_{95}=1$ neutral; scale spans $3.2\times10^{-3}$ to $64$). Cell edges sit at the logarithmic
midpoints between neighbouring $g_t$ values and at the midpoints between columns, so no colour is
interpolated. The 20 → 30 GeV step is therefore drawn as a hard edge at 25 GeV, but the change it
represents is physical.

| $M_V$ | points | excluded | median $\mu_{95}$ | $\mu_{95}$ range | median $\mathrm{BR_{inv}}$ |
|---|---|---|---|---|---|
| 20 | 44 | 1 | 3.66 | 0.94 – 64 (cap) | 0.018 |
| 30 | 44 | 34 | 0.405 | 0.099 – 2.93 | 0.580 |

**Mechanism.** At fixed $g_t$ the dark coupling is larger in the 30 GeV column by a median factor
8.38 (range 7.95–9.73 over the 44 matched couplings), because
$g_\chi=\kappa(m_\chi)M_V^2/g_t$: $\kappa$ rises from $1.25\times10^{-5}$ to $4.94\times10^{-5}$
(×3.95) and $M_V^2$ by ×2.25, giving ×8.9. The larger $g_\chi$ keeps the invisible channel open at
30 GeV, where at 20 GeV it has already collapsed:

| $g_t$ | $g_\chi$ 20 / 30 | $\mathrm{BR_{inv}}$ 20 / 30 | $\mu_{95}$ 20 / 30 | ratio |
|---|---|---|---|---|
| 0.100 | 0.049 / 0.475 | 0.957 / 1.000 | 3.23 / 2.93 | 1.1 |
| 0.194 | 0.024 / 0.235 | 0.600 / 0.993 | 1.33 / 0.671 | 2.0 |
| 0.377 | 0.013 / 0.114 | 0.098 / 0.900 | 1.45 / 0.230 | 6.3 |
| 0.733 | 0.007 / 0.057 | 0.008 / 0.377 | 4.09 / 0.135 | 30.3 |
| 1.423 | 0.004 / 0.031 | 0.001 / 0.044 | 11.24 / 0.275 | 40.9 |
| 3.545 | 0.002 / 0.013 | 0.000 / 0.001 | 64.0 (cap) / 1.45 | 44.1 |

The step is therefore *largest* where the 20 GeV column has already lost its invisible signal, and
there its values are pinned at the scan cap: 8 of the 44 points sit at $\mu_{95}=64$.

**Threshold is not the driver.** $2m_\chi/M_V$ is 0.86 at 20 GeV and 0.84 at 30 GeV (medians), so
phase space barely changes. Within each column $\Gamma_{\rm inv}\propto g_\chi^2$ and
$\Gamma_{\rm vis}\propto g_t^2$ with fitted slopes 1.98–2.02, and feeding the 20 GeV width
coefficients into the 30 GeV couplings reproduces the 30 GeV $\mathrm{BR_{inv}}$ to 1–3%. The BR
difference is entirely coupling-driven.

Caveat on $\kappa$: it is **not** monotonic across the grid — it peaks at 30 GeV
($1.25,\ 4.94,\ 3.15,\ 2.55,\dots\times10^{-5}$). The ×3.95 used above is specific to the 20 → 30
pair, where $\kappa(20)$ is the global minimum; it is not a trend with $M_V$.

## 2. The 25 GeV curve — rejected

$\mu_{95}(25)$ would have to be $\sqrt{\mu_{95}(20)\mu_{95}(30)}$ at fixed $g_t$. That is not a
computed number, and it fails three tests:

1. **It contradicts the manuscript**, which states that no line is drawn across the 20–30 GeV
   interval (Section 5.2). Fig. 3 would draw exactly that line.
2. **It is cap-driven over half its range.** For $g_t>1.98$ both endpoints include censored values,
   so the curve plateaus at 6–10 and that plateau scales as $\sqrt{\rm cap}$.
3. **It manufactures a physics claim.** The curve crosses $\mu_{95}=1$ at $g_t\approx0.94$, implying
   a window closing at 25 GeV a factor 2.9 below the 30 GeV closure, built from two limits a factor
   27 apart. A geometric mean of two CLs limits that far apart has no statistical meaning.

$\sqrt{\mu_{20}\mu_{30}}$ is also the arithmetic midpoint, not the logarithmic interpolation it was
labelled as: 25 GeV sits at 0.55 of the log interval, so the log-linear value
$\mu_{20}^{0.45}\mu_{30}^{0.55}$ is up to 19% lower.

If the transition must be shown, the alternatives are a real 25 GeV column (44 points, one
MG5+Pythia+Delphes sample each) or shading the band between the 20 and 30 GeV curves.

## 3. Files

| file | what |
|---|---|
| `fig2_v10.pdf/.png` | the exclusion map, with cap markers |
| `fig3_v10.pdf/.png` | $\mu_{95}(g_t)$, six computed columns |
| `column_stats.csv` | per-column counts, medians, $\mathrm{BR_{inv}}$, $2m_\chi/M_V$ |
| `GRID_V10.csv` | the 470-point grid |
| `make_fig2_v10.py`, `make_figs_v10.py` | plotting scripts |

## 4. Changes made in response

| finding | action |
|---|---|
| Capped cells (8, all at 20 GeV) coloured as ordinary data in Fig. 2 | open circles + legend entry, as in Fig. 3 |
| Fig. 3 drew a line the text says is not drawn | 25 GeV curve removed; caption back to "six mediator masses" |
| Cap quoted as ">60" while the grid is pinned at 64.0 | $\mu_{95}=64$ in Section 5.1, Table 2 row and caption, Fig. 3 caption |
| Script comment quoted the 20 GeV island as 0.85–0.89 | corrected to 0.94–1.00 (grid minimum 0.9384) |
| Claim "factor 9.5" / "both $\kappa$ and $M_V^2$ grow" | restated as 8.38 median for this pair, $\kappa$ non-monotonic |
| Mechanism table sampled only $g_t=0.15$–0.29, the weakest part of the step | resampled, table above |

`column_stats.csv` reproduces every column statistic from `GRID_V10.csv` exactly (14 rows, all
quantities).
